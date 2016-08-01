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
from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.dedup.rehash import main

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
        def build_activity_message(type_, num_of_duplicates):
            if num_of_duplicates:
                return 'Deduped %d %s ' % (num_of_duplicates, type_)
            else:
                return "No %s duplicates found" % type_

        messages = []
        elapsed = StopWatch()
        try:
            main()
            STIXPurge.wait_for_background_jobs_completion(datetime.utcnow())

            for object_type in STIXDedup.OBJECT_TYPES:
                cursor = STIXDedup.find_duplicates(object_type, self.config.only_local_ns)
                for original, duplicates in cursor.iteritems():
                    try:
                        self.merge_object(original, duplicates)
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

    def remap_objects(self, duplicates):
        ip = DedupInboxProcessor(user=self.user, validate=True)
        for dup in duplicates:
            try:
                api_obj, tlp, esms, etou = STIXDedup.load_eo(dup)
                ip.add(InboxItem(api_object=api_obj, etlp=tlp, esms=esms, etou=etou))
            except InboxError as e:
                log_error(e, 'adapters/dedup/dedup', 'Adding object %s to IP failed' % dup)
        get_db().stix.remove({'_id': {
            '$in': duplicates}})
        try:
            ip.run()
        except Exception as e:
            log_error(e, 'adapters/dedup/dedup', 'Inboxing objects failed')

    def remap_parent_objects(self, parents, map_table):
        if parents:
            ip = InboxProcessor(user=self.user, trustgroups=None)
            for id_, type_ in parents.iteritems():
                try:
                    api_obj, tlp, esms, etou = STIXDedup.load_eo(id_)
                    api_obj = api_obj.remap(map_table)
                    ip.add(InboxItem(api_object=api_obj, etlp=tlp, esms=esms, etou=etou))
                except InboxError as e:
                    log_error(e, 'adapters/dedup/dedup', 'Adding parent %s to IP failed' % id_)
                    pass
            try:
                ip.run()
            except InboxError as e:
                log_error(e, 'adapters/dedup/dedup', 'Remapping parent objects failed')

    @staticmethod
    def remap_edges(original, duplicates):
        backlinks_to_update = {}
        for dup in duplicates:
            edges_of_duplicate = EdgeObject.load(dup).to_ApiObject().edges()
            for edge in edges_of_duplicate:
                try:
                    edge_id = edge.idref
                    backlinks_to_update[edge_id] = StixBacklink.objects.get(id=edge_id).edges
                    backlinks_to_update[edge_id][original] = backlinks_to_update[edge_id].pop(dup)
                except DoesNotExist as e:
                    pass
                except Exception as e:
                    log_error(e, 'adapters/dedup/dedup', 'Finding parents for %s failed' % edge.idref)
                    pass
        for id_, backlinks in backlinks_to_update.iteritems():
            get_db().stix_backlinks.update({'_id': id_}, {'$set': {'value': backlinks}}, upsert=True)

    @staticmethod
    def remap_backlinks(original, duplicates):
        parents_of_original, parents_of_duplicate = STIXDedup.calculate_backlinks(original, duplicates)

        new_parents = parents_of_duplicate.copy()
        new_parents.update(parents_of_original)
        if new_parents:
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

    def merge_object(self, original, duplicates):
        parents_of_duplicates = STIXDedup.calculate_backlinks(original, duplicates)[1]

        STIXDedup.remap_backlinks(original, duplicates)
        STIXDedup.remap_edges(original, duplicates)

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
