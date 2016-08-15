import os
import operator

from django.conf import settings
from mongoengine.connection import get_db
from mongoengine.errors import DoesNotExist
from pymongo.errors import PyMongoError
from datetime import datetime
from edge import LOCAL_ALIAS
from edge.tools import StopWatch, rgetattr
from edge.generic import EdgeObject
from edge.inbox import InboxError, InboxProcessor, InboxItem
from edge.models import StixBacklink
from users.models import Repository_User
from adapters.certuk_mod.dedup.DedupInboxProcessor import _existing_title_and_capecs, \
    _existing_tgts_with_cves, _update_existing_objects, _update_existing_properties, _get_sighting_count, \
    add_additional_file_hashes
from adapters.certuk_mod.common.activity import save as log_activity
from adapters.certuk_mod.common.logger import log_error
import adapters.certuk_mod.dedup.rehash as rehash

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')

if not hasattr(settings, 'BASE_DIR'):
    raise Exception('Failed to import Django settings')


class STIXDedup(object):
    HASH_MAP = {'RED': 4, 'AMBER': 3, 'GREEN': 2, 'WHITE': 1, 'NULL': 0}
    LOCAL_ALIAS_REGEX = '^%s:' % LOCAL_ALIAS
    OBJECT_TYPES = ['ttp', 'tgt', 'obs']
    NAME_TYPES = {'obs': 'Observable', 'ttp': 'TTP', 'tgt': 'Exploit Target'}

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
                    rehash.main(last_run_at)
                cursor = STIXDedup.find_duplicates(object_type, self.config.only_local_ns)
                for original, duplicates in cursor.iteritems():
                    try:
                        self.merge_object(original, duplicates, object_type)
                    except Exception as e:
                        log_activity('system', 'DEDUP', 'ERROR', e.message)
                messages.append(build_activity_message(object_type, len(cursor)))
            messages.insert(0, 'Online Dedup (in %dms): ' % int(elapsed.ms()))
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
    def get_additional_sightings_count(original, duplicates):
        additional_sightings = {}
        for dup in duplicates:
            api_object = EdgeObject.load(dup).to_ApiObject()
            additional_sightings[original] = additional_sightings.get(original, 0) + _get_sighting_count(api_object.obj)
        return additional_sightings

    @staticmethod
    def get_additional_file_hashes(original, duplicates):
        additional_file_hashes = {}
        api_object = EdgeObject.load(original).to_ApiObject()
        if rgetattr(api_object, STIXDedup.PROPERTY_TYPE, None) == 'FileObjectType':
            for dup in duplicates:
                api_obj, tlp, esms, etou = STIXDedup.load_eo(dup)
                io = InboxItem(api_object=api_obj, etlp=tlp, esms=esms, etou=etou)
                add_additional_file_hashes(io, additional_file_hashes, original)
        return additional_file_hashes

    def update_existing_properties_on_original(self, original, duplicates, duplicates_edges,
                                               type_):
        if type_ == 'tgt' or 'ttp':
            _update_existing_objects(duplicates_edges, self.user)
            get_db().stix.remove({'_id': {
                '$in': duplicates}})
        elif type_ == 'obs':
            additional_sightings = STIXDedup.get_additional_sightings_count(original, duplicates)
            additional_file_hashes = STIXDedup.get_additional_file_hashes(original, duplicates)
            _update_existing_properties(additional_sightings, additional_file_hashes, self.user)
            get_db().stix.remove({'_id': {
                '$in': duplicates}})

    def remap_duplicates_parents(self, parents,
                                 map_table):  # Inbox parents of duplicates remapping duplicate reference to original
        if parents:
            ip = InboxProcessor(user=self.user, trustgroups=None)
            for id_, type_ in parents.iteritems():
                try:
                    api_obj, tlp, esms, etou = STIXDedup.load_eo(id_)
                    api_obj = api_obj.remap(map_table)
                    ip.add(InboxItem(api_object=api_obj, etlp=tlp, esms=esms, etou=etou))
                except InboxError as e:
                    log_error(e, 'adapters/dedup/dedup', 'Adding parent %s to IP failed' % id_)
            try:
                ip.run()
            except InboxError as e:
                log_error(e, 'adapters/dedup/dedup', 'Remapping parent objects failed')

    @staticmethod  # Update backlinks for duplicates edges.
    def remap_backlinks_for_edges_of_duplicates(original, duplicates, duplicates_edges):
        backlinks_to_update = {}
        for edge in duplicates_edges[original]:
            edge_id = edge.idref
            if edge_id != original and edge_id not in duplicates:  # If opposite is true, dup references original
                # or dup references another dup. Remapping results in external references being left in backlinks
                try:
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

        new_parents = parents_of_duplicate.copy()
        new_parents.update(parents_of_original)
        for dup in duplicates:  # Strip out references to duplicates in updated backlinks
            if dup in new_parents:
                del new_parents[dup]
        try:
            get_db().stix_backlinks.update({'_id': original}, {'$set': {'value': new_parents}}, upsert=True)
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

    @staticmethod  # duplicates_edges = {original: [edges]}
    def calculate_edges_of_duplicates(original, duplicates):
        duplicates_edges = {}
        for dup in duplicates:
            edges_of_duplicates = EdgeObject.load(dup).to_ApiObject().edges()
            for edge in edges_of_duplicates:
                duplicates_edges.setdefault(original, []).append(edge)
        return duplicates_edges

    def merge_object(self, original, duplicates, type_):
        duplicates_edges = STIXDedup.calculate_edges_of_duplicates(original, duplicates)
        parents_of_duplicates = STIXDedup.calculate_backlinks(original, duplicates)[1]

        STIXDedup.remap_backlinks_for_original(original, duplicates)
        STIXDedup.remap_backlinks_for_edges_of_duplicates(original, duplicates, duplicates_edges)

        map_table = {dup: original for dup in duplicates}
        self.remap_duplicates_parents(parents_of_duplicates, map_table)
        self.update_existing_properties_on_original(original, duplicates, duplicates_edges, type_)

    @staticmethod
    def find_duplicates(type_, local):
        if local:
            namespace_query = {'_id': {'$regex': STIXDedup.LOCAL_ALIAS_REGEX}, 'type': type_}
        else:
            namespace_query = {'type': type_}

        def obs_transform(cursor):  # If duplicates have more than one tlpLevel take the most permissive
            obs = {}
            for row in cursor:
                if len(row.get('tlpLevels')) > 1:
                    tlps = row.get('tlpLevels')
                    map_tlps = {}
                    for tlp in tlps:
                        if STIXDedup.HASH_MAP.get(tlp):
                            map_tlps[tlp] = STIXDedup.HASH_MAP.get(tlp)
                    tlp_level = sorted(map_tlps.items(), key=operator.itemgetter(1))[0][0]
                    id_ = STIXDedup.match_tlp_hash(row.get('_id'), tlp_level).get('_id')
                    ids = row.get('uniqueIds')
                    ids.pop(ids.index(id_))
                    obs[id_] = ids
                else:
                    obs[row.get('uniqueIds')[0]] = row.get('uniqueIds')[1:]
            return obs

        def ttp_tgt_transform(cursor):
            original_to_duplicates = {}
            for row in cursor.values():
                if len(row) > 1:
                    master = row[0]
                    original_to_duplicates[master] = row[1:]
            return original_to_duplicates

        if type_ == 'obs':
            return obs_transform(STIXDedup.obs_hash_match(namespace_query))
        elif type_ == 'ttp':
            return ttp_tgt_transform(_existing_title_and_capecs(local))
        elif type_ == 'tgt':
            return ttp_tgt_transform(_existing_tgts_with_cves(local))

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
            return {'_id': doc('_id')}

        return transform(get_db().stix.find_one({
            'data.hash': hash_,
            'data.etlp': tlp_level
        }))

    @staticmethod
    def file_obs_hash_match():
        cursor = get_db().stix.aggregate([
            {
                '$match': {
                    'data.summary.type': 'FileObjectType'
                }
            }
        ])
