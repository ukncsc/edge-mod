import os
import operator

from django.conf import settings
from mongoengine.connection import get_db
from mongoengine.errors import DoesNotExist
from pymongo.errors import PyMongoError
from datetime import datetime
from edge import LOCAL_ALIAS
from edge.tools import StopWatch
from edge.generic import EdgeObject
from edge.inbox import InboxError, InboxProcessor, InboxItem
from edge.models import StixBacklink
from users.models import Repository_User
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor, _existing_title_and_capecs, \
    _existing_tgts_with_cves
from adapters.certuk_mod.retention.purge import STIXPurge
from adapters.certuk_mod.common.activity import save as log_activity

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')

if not hasattr(settings, 'BASE_DIR'):
    raise Exception('Failed to import Django settings')


class STIXDedup(object):
    HASH_MAP = {'RED': 4, 'AMBER': 3, 'GREEN': 2, 'WHITE': 1, 'NULL': 0}
    LOCAL_ALIAS_REGEX = '^%s:' % LOCAL_ALIAS
    OBJECT_TYPES = ['ttp', 'tgt', 'obs']

    def __init__(self, dedup_config):
        self.config = dedup_config
        self.user = Repository_User.objects.get(username='system')

    def run(self):
        def build_activity_message(type_, num_of_duplicates, time):
            if num_of_duplicates:
                return 'Deduped %d %s based on hashes in %dms' % (num_of_duplicates, type_, time)
            else:
                return "No %s duplicates found" % (type_)

        messages = []
        elapsed = StopWatch()
        try:
            current_date = datetime.utcnow()
            STIXPurge.wait_for_background_jobs_completion(current_date)

            for object_type in STIXDedup.OBJECT_TYPES:
                cursor = STIXDedup.find_duplicates(object_type, self.config.only_local_ns)
                for original, duplicates in cursor.iteritems():
                    try:
                        self.merge_object(original, duplicates)
                        messages.append(build_activity_message(object_type, len(original), int(elapsed.ms())))
                    except Exception as e:
                        log_activity('system', 'DEDUP', 'ERROR', e.message)
            log_activity('system', 'DEDUP', 'INFO', "\n".join(messages))
        except Exception as e:
            log_activity('system', 'DEDUP', 'ERROR', e.message)

    @staticmethod
    def load_eo(id_):
        eo = EdgeObject.load(id_)
        tlp = eo.etlp if hasattr(eo, 'etlp') else 'NULL'
        esms = eo.esms if hasattr(eo, 'esms') else ''
        api_obj = eo.to_ApiObject()
        return api_obj, tlp, esms

    def remap_objects(self, duplicates):
        ip = DedupInboxProcessor(user=self.user, validate=True)
        for dup in duplicates:
            try:
                api_obj, tlp, esms = STIXDedup.load_eo(dup)
                ip.add(InboxItem(api_object=api_obj, etlp=tlp, esms=esms))
            except InboxError as e:
                raise e
        get_db().stix.remove({'_id': {
            '$in': duplicates}})
        ip.run()

    def remap_parent_objects(self, parents, map_table):
        if parents:
            ip = InboxProcessor(user=self.user, trustgroups=None)
            for id_, type_ in parents.iteritems():
                try:
                    api_obj, tlp, esms = STIXDedup.load_eo(id_)
                    api_obj = api_obj.remap(map_table)
                    ip.add(InboxItem(api_object=api_obj, etlp=tlp, esms=esms))
                except InboxError as e:
                    raise e
            try:
                ip.run()
            except InboxError as e:
                raise e

    @staticmethod
    def remap_backlinks(original, duplicate):
        parents_of_original, parents_of_duplicate = STIXDedup.calculate_backlinks(original, duplicate)

        new_parents = parents_of_duplicate.copy()
        new_parents.update(parents_of_original)
        if new_parents:
            try:
                get_db().stix_backlinks.update({'_id': original}, {'$set': {'value': new_parents}}, upsert=True)
            except PyMongoError as pme:
                raise pme
        if parents_of_duplicate:
            try:
                get_db().stix_backlinks.remove({'_id': {'$in': duplicate}})
            except PyMongoError as pme:
                raise pme

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
        STIXDedup.remap_backlinks(original, duplicates)

        map_table = {dup: original for dup in duplicates}
        self.remap_parent_objects(parents_of_duplicates, map_table)

        self.remap_objects(duplicates)

    @classmethod
    def find_duplicates(cls, type_, local):
        if local:
            namespace_query = {'_id': {'$regex': cls.LOCAL_ALIAS_REGEX}, 'type': type_}
        else:
            namespace_query = {'type': type_}

        def obs_transform(cursor):
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
            for row in cursor.items():
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
            },
            {
                '$sort': {
                    'count': 1
                }
            }
        ], cursor={})

    @staticmethod
    def match_tlp_hash(hash_, tlp_level):
        def transform(cursor):
            return {'_id': row.get('_id') for row in cursor}

        return transform(get_db().stix.find({
            'data.hash': hash_,
            'data.etlp': tlp_level
        }))
