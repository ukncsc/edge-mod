import os
import operator

from django.conf import settings
from mongoengine.connection import get_db
from mongoengine.errors import DoesNotExist
from pymongo.errors import PyMongoError
from datetime import datetime
from edge import LOCAL_ALIAS
from edge.tools import StopWatch, rgetattr
from edge.generic import EdgeObject, EdgeError
from edge.inbox import InboxError, InboxProcessor, InboxItem
from edge.models import StixBacklink
from users.models import Repository_User
from adapters.certuk_mod.dedup.DedupInboxProcessor import _existing_title_and_capecs, \
    _existing_tgts_with_cves, _update_existing_objects, _update_existing_properties, _get_sighting_count, \
    add_additional_file_hashes, _has_matching_file_hash
from adapters.certuk_mod.common.activity import save as log_activity
from adapters.certuk_mod.common.logger import log_error
import adapters.certuk_mod.dedup.rehash as rehash

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')

if not hasattr(settings, 'BASE_DIR'):
    raise Exception('Failed to import Django settings')


class STIXDedup(object):
    TLP_MAP = {'RED': 4, 'AMBER': 3, 'GREEN': 2, 'WHITE': 1, 'NULL': 0}
    LOCAL_ALIAS_REGEX = '^%s:' % LOCAL_ALIAS
    OBJECT_TYPES = ['obs']  # ['ttp', 'tgt', 'obs']
    NAME_TYPES = {'obs': 'Observables'}  # {'obs': 'Observable', 'ttp': 'TTP', 'tgt': 'Exploit Target'}

    PROPERTY_TYPE = ['obj', 'object_', 'properties', '_XSI_TYPE']

    def __init__(self, dedup_config):
        self.config = dedup_config
        self.user = Repository_User.objects.get(username='system')

    def run(self):
        def build_activity_message(type_, num_of_duplicates):
            if num_of_duplicates:
                return 'Deduped %d %s ' % (num_of_duplicates, self.NAME_TYPES[type_])
            else:
                return "No %s duplicates found" % self.NAME_TYPES[type_]

        messages = []
        last_run_at = self.config.task.last_run_at
        elapsed = StopWatch()
        try:
            for object_type in self.OBJECT_TYPES:
                if object_type == 'obs':
                    try:
                        rehash.rehash(last_run_at)
                    except:
                        pass  # rehash failed, let's just continue with the hashes as is.
                original_to_duplicates = STIXDedup.find_duplicates(object_type, self.config.only_local_ns)
                for original, duplicates in original_to_duplicates.iteritems():
                    try:
                        self.merge_object(original, duplicates, object_type)
                    except Exception as e:
                        log_error(e, 'adapters/dedup/dedup', 'Failed to merge %s' % original)
                messages.append(build_activity_message(object_type, len(original_to_duplicates)))
            messages.insert(0, 'Online Dedup in %ds: ' % int(elapsed.sec()))
            log_activity('system', 'DEDUP', 'INFO', "\n \t".join(messages))
        except Exception as e:
            log_activity('system', 'DEDUP', 'ERROR', e.message)

    @staticmethod
    def load_eo(id_):
        eo = EdgeObject.load(id_)
        tlp = eo.etlp if hasattr(eo, 'etlp') else 'NULL'
        esms = eo.esms if hasattr(eo, 'esms') else []
        etou = eo.etou if hasattr(eo, 'etou') else []
        api_obj = eo.to_ApiObject()
        return api_obj, tlp, esms, etou

    @staticmethod
    def get_additional_sightings_count(duplicates):
        count = 0
        for dup in duplicates:
            api_object = EdgeObject.load(dup).to_ApiObject()
            count += _get_sighting_count(api_object.obj)
        return count

    @staticmethod
    def get_additional_file_hashes(original, duplicates):
        additional_file_hashes = {}
        api_object = EdgeObject.load(original).to_ApiObject()
        if rgetattr(api_object, STIXDedup.PROPERTY_TYPE, None) == 'FileObjectType':
            for dup in duplicates:
                try:
                    api_obj, tlp, esms, etou = STIXDedup.load_eo(dup)
                except EdgeError as e:
                    continue
                io = InboxItem(api_object=api_obj, etlp=tlp, esms=esms, etou=etou)
                add_additional_file_hashes(io, additional_file_hashes, original)
        return additional_file_hashes

    def update_existing_properties_on_original(self, original, duplicates, type_):

        if type_ == 'obs':
            additional_sightings = STIXDedup.get_additional_sightings_count(duplicates)
            additional_file_hashes = STIXDedup.get_additional_file_hashes(original, duplicates)
            _update_existing_properties({original: additional_sightings}, additional_file_hashes, self.user)
        # elif type_ == 'tgt' or type_ == 'ttp':
        #     if duplicates:
        #         _update_existing_objects(duplicates_edges, self.user)
        #     get_db().stix.remove({'_id': {
        #         '$in': duplicates}})

    @staticmethod
    def remove_duplicates(duplicates):
        get_db().stix.remove({'_id': {
                '$in': duplicates}})

    def remap_duplicates_parents(self, parents,
                                 map_table):  # Inbox parents of duplicates remapping duplicate reference to original
        if parents:
            ip = InboxProcessor(user=self.user, trustgroups=None)
            for id_, type_ in parents.iteritems():
                try:
                    api_obj, tlp, esms, etou = STIXDedup.load_eo(id_)
                except EdgeError as e:  # Parent may not exist in Edge but has a record in the STIX BLs collection
                    continue
                try:
                    api_obj = api_obj.remap(map_table)
                    ip.add(InboxItem(api_object=api_obj, etlp=tlp, esms=esms, etou=etou))
                except InboxError as e:
                    log_error(e, 'adapters/dedup/dedup', 'Adding parent %s to IP failed' % id_)
                    continue
            try:
                ip.run()
            except InboxError as e:
                log_error(e, 'adapters/dedup/dedup', 'Remapping parent objects failed')

    @staticmethod  # Update backlinks for duplicates edges.
    def remap_backlinks_for_edges_of_duplicates(original, duplicates, duplicates_edges):
        backlinks_to_update = {}
        edges_already_done = []
        if duplicates_edges:
            for edge in duplicates_edges.get(original, []):
                edge_id = edge.idref
                if edge_id != original and edge_id not in duplicates and edge_id not in edges_already_done:  # If opposite is true, dup references original
                    # or dup references another dup. Remapping results in external references being left in backlinks
                    try:
                        edges_already_done.append(edge_id)
                        backlinks_to_update[edge_id] = StixBacklink.objects.get(id=edge_id).edges
                        for dup in duplicates:
                            if dup in backlinks_to_update[edge_id]:
                                backlinks_to_update[edge_id][original] = backlinks_to_update[edge_id].pop(dup)
                    except DoesNotExist as e:
                        pass
                    except Exception as e:
                        log_error(e, 'adapters/dedup/dedup', 'Finding parents for %s failed' % edge_id)
        for id_, backlinks in backlinks_to_update.iteritems():
            get_db().stix_backlinks.update({'_id': id_}, {'$set': {'value': backlinks}}, upsert=True)

    @staticmethod  # If duplicates have any backlinks update these to refer to original
    def remap_backlinks_for_original(original, duplicates):
        parents_of_original, parents_of_duplicate = STIXDedup.calculate_backlinks(original, duplicates)

        parents_of_original.update(parents_of_duplicate)
        for dup in duplicates:  # Strip out references to duplicates in updated backlinks
            if dup in parents_of_original:
                del parents_of_original[dup]
        try:
            get_db().stix_backlinks.update({'_id': original}, {'$set': {'value': parents_of_original}}, upsert=True)
        except PyMongoError as pme:
            log_error(pme, 'adapters/dedup/dedup', 'Updating backlinks failed')
        if parents_of_duplicate:
            try:
                get_db().stix_backlinks.remove({'_id': {'$in': duplicates}})
            except PyMongoError as pme:
                log_error(pme, 'adapters/dedup/dedup', 'Removing parent backlinks failed')

    @staticmethod
    def calculate_backlinks(original, duplicates):
        parents_of_original, parents_of_duplicate = {}, {}
        try:
            parents_of_original = StixBacklink.objects.get(id=original).edges
        except DoesNotExist as e:
            pass
        for dup in duplicates:
            try:
                parents_of_duplicate.update(StixBacklink.objects.get(id=dup).edges)
            except DoesNotExist as e:
                pass
        return parents_of_original, parents_of_duplicate

    @staticmethod
    def could_have_edges(eo):
        if eo.ty == 'ttp' or eo.ty == 'tgt' or eo.summary.get('type') == 'ObservableComposition':
            return True
        else:
            return False

    @staticmethod  # duplicates_edges = {original: [edges]}
    def calculate_edges_of_duplicates(original, duplicates):
        duplicates_edges = {}
        if not STIXDedup.could_have_edges(EdgeObject.load(original)):
            return duplicates_edges
        for dup in duplicates:
            edges_of_duplicates = EdgeObject.load(dup).to_ApiObject().edges()
            for edge in edges_of_duplicates:
                duplicates_edges.setdefault(original, []).append(edge)
        return duplicates_edges

    def merge_object(self, original, duplicates, type_):
        duplicates_edges = STIXDedup.calculate_edges_of_duplicates(original, duplicates)
        parents_of_duplicates = STIXDedup.calculate_backlinks(original, duplicates)[1]
        map_table = {dup: original for dup in duplicates}

        self.remap_duplicates_parents(parents_of_duplicates, map_table)
        self.update_existing_properties_on_original(original, duplicates, type_)

        STIXDedup.remap_backlinks_for_original(original, duplicates)
        STIXDedup.remap_backlinks_for_edges_of_duplicates(original, duplicates, duplicates_edges)

        STIXDedup.remove_duplicates(duplicates)

    @staticmethod
    def find_duplicates(type_, local):
        def obs_transform(matches):  # If duplicates have more than one tlpLevel take the most permissive
            def get_lowest_tlp(match):
                tlps = match.get('tlpLevels')
                map_tlps = {}
                for tlp in tlps:
                    if STIXDedup.TLP_MAP.get(tlp):
                        map_tlps[tlp] = STIXDedup.TLP_MAP.get(tlp)
                tlp_level = sorted(map_tlps.items(), key=operator.itemgetter(1))[0][0]
                return tlp_level

            obs = {}
            for match in matches:
                if len(match.get('tlpLevels')) > 1:
                    lowest_tlp = get_lowest_tlp(match)
                    id_ = STIXDedup.match_tlp_hash(match.get('_id'), lowest_tlp).get('_id')
                    ids = match.get('uniqueIds')
                    del ids[ids.index(id_)]
                    obs[id_] = ids
                else:
                    obs[match.get('uniqueIds')[0]] = match.get('uniqueIds')[1:]
            return obs

        # def ttp_tgt_transform(matches):
        #     original_to_duplicates = {}
        #     for row in matches.values():
        #         if len(row) > 1:
        #             master = row[0]
        #             original_to_duplicates[master] = row[1:]
        #     return original_to_duplicates

        if type_ == 'obs':
            namespace_query = {'type': type_, 'data.summary.type': {
                '$ne': 'FileObjectType'}}
            if local:
                namespace_query.update({'_id': {'$regex': STIXDedup.LOCAL_ALIAS_REGEX}})
            matches = obs_transform(STIXDedup.obs_hash_match(namespace_query))
            matches.update(STIXDedup.file_obs_match(namespace_query))
            return matches
        # elif type_ == 'ttp':
        #     return ttp_tgt_transform(_existing_title_and_capecs(local))
        # elif type_ == 'tgt':
        #     return ttp_tgt_transform(_existing_tgts_with_cves(local))

    @staticmethod
    def obs_hash_match(namespace_query):
        return get_db().stix.aggregate([
            {
                '$match': namespace_query
            },
            {
                '$sort': {
                    'created_on': -1
                }
            },
            {
                '$group': {
                    '_id': '$data.hash',
                    'uniqueIds': {
                        '$addToSet': '$_id'
                    },
                    'tlpLevels': {
                        '$addToSet': '$data.etlp'
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$match': {
                    'count': {'$gt': 1}
                }
            }
        ], cursor={}, allowDiskUse=True)

    @staticmethod
    def match_tlp_hash(hash_, tlp_level):
        def transform(doc):
            return {'_id': doc['_id']}

        return transform(get_db().stix.find_one({
            'data.hash': hash_,
            'data.etlp': tlp_level
        }))

    @staticmethod
    def file_obs_match(namespace_query):
        namespace_query.update({'data.summary.type': 'FileObjectType'})
        # 'data.summary.value' field stores the file name for File Observables.
        matches = get_db().stix.aggregate([
            {
                '$match': namespace_query
            },
            {
                '$sort': {
                    'created_on': -1
                }
            },
            {
                '$group': {
                    '_id': '$data.summary.value',
                    'ids': {
                        '$push': '$_id'
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$match': {
                    'count': {'$gt': 1}
                }
            }
        ], cursor={})

        # Compare each File Obs matched on file name. Compare each to see if they also have a matching file hash
        # If true take the File Obs with the most permissive TLP as we do for other Observables.
        complete_map_table = {}
        for doc in matches:
            _map_table = {}
            _matching_key_objects = {}

            for id_ in doc['ids']:
                try:
                    id_ao, tlp, esms, etou = STIXDedup.load_eo(id_)
                except EdgeError as e:
                    continue
                matching_key = None
                for key in _map_table.keys():
                    key_ao = _matching_key_objects[key]['ao']
                    if _has_matching_file_hash(id_ao, key_ao):
                        matching_key = key
                        break
                if matching_key:
                    key_tlp = _matching_key_objects[key]['tlp']
                    if STIXDedup.TLP_MAP[tlp] < STIXDedup.TLP_MAP[key_tlp]:
                        _map_table[id_] = _map_table[matching_key]
                        _map_table[id_].append(matching_key)
                        del _map_table[matching_key]
                        del _matching_key_objects[matching_key]
                        _matching_key_objects.setdefault(id_, {"ao": id_ao, "tlp": tlp})
                    else:
                        _map_table[matching_key].append(id_)
                else:
                    _map_table[id_] = []
                    _matching_key_objects.setdefault(id_, {"ao": id_ao, "tlp": tlp})
            for key, value in _map_table.iteritems():
                if len(value):
                    complete_map_table[key] = value

        return complete_map_table
