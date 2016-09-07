import os
import operator

from django.conf import settings
from mongoengine.connection import get_db
from mongoengine.errors import DoesNotExist
from pymongo.errors import PyMongoError
from edge import LOCAL_ALIAS
from edge.tools import StopWatch, rgetattr
from edge.generic import EdgeObject, EdgeError
from edge.inbox import InboxError, InboxProcessor, InboxItem
from edge.models import StixBacklink
from users.models import Repository_User
from adapters.certuk_mod.dedup.DedupInboxProcessor import _update_existing_properties, _get_sighting_count, \
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
    PROPERTY_TYPE = ['obj', 'object_', 'properties', '_XSI_TYPE']

    def __init__(self, dedup_config):
        self.config = dedup_config
        self.user = Repository_User.objects.get(username='system')

    def run(self):
        def build_activity_message(num_of_duplicates):
            if num_of_duplicates:
                return 'Deduped %d Observables ' % (num_of_duplicates)
            else:
                return "No Observable duplicates found"

        messages = []
        last_run_at = self.config.task.last_run_at
        elapsed = StopWatch()
        try:
            try:
                rehash.rehash(last_run_at)
            except:
                pass  # rehash failed, let's just continue with the hashes as is.

            original_to_duplicates = STIXDedup.find_duplicates(self.config.only_local_ns)
            for original, duplicates in original_to_duplicates.iteritems():
                try:
                    self.merge_object(original, duplicates)
                except Exception as e:
                    log_error(e, 'adapters/dedup/dedup', 'Failed to merge %s' % original)

            messages.append(build_activity_message(len(original_to_duplicates)))
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

    def update_existing_properties_on_original(self, original, duplicates):
        additional_sightings = STIXDedup.get_additional_sightings_count(duplicates)
        additional_file_hashes = STIXDedup.get_additional_file_hashes(original, duplicates)
        tlp_level = STIXDedup.load_eo(original)[1]
        _update_existing_properties({original: additional_sightings}, additional_file_hashes, self.user, {original: tlp_level})

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

    def merge_object(self, original, duplicates):
        parents_of_duplicates = STIXDedup.calculate_backlinks(original, duplicates)[1]
        map_table = {dup: original for dup in duplicates}

        self.remap_duplicates_parents(parents_of_duplicates, map_table)
        self.update_existing_properties_on_original(original, duplicates)

        STIXDedup.remap_backlinks_for_original(original, duplicates)
        STIXDedup.remove_duplicates(duplicates)

    @staticmethod
    def find_duplicates(local):
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

        namespace_query = {}
        if local:
            namespace_query.update({'_id': {'$regex': STIXDedup.LOCAL_ALIAS_REGEX}})
        matches = obs_transform(STIXDedup.obs_hash_match(namespace_query))
        matches.update(STIXDedup.file_obs_match(namespace_query))
        return matches

    @staticmethod
    def obs_hash_match(namespace_query):
        namespace_query.update(
            {'type': 'obs', 'data.summary.type': {'$nin': ['FileObjectType', 'ObservableComposition']}})
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
        namespace_query.update({'type': 'obs', 'data.summary.type': 'FileObjectType'})
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
        ], cursor={}, allowDiskUse=True)

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
