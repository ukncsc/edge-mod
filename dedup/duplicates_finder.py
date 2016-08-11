import os
import operator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings

if not hasattr(settings, 'BASE_DIR'):
    raise Exception("Failed to import Django settings")
from edge import LOCAL_ALIAS
from mongoengine.connection import get_db

LOCAL_ALIAS_REGEX = '^%s:' % LOCAL_ALIAS
HASH_MAP = {'RED': 4, 'AMBER': 3, 'GREEN': 2, 'WHITE': 1, 'NULL': 0}


def find_duplicates(type_, local):
    if local:
        namespace_query = {'_id': {'$regex': LOCAL_ALIAS_REGEX}, 'type': type_}
    else:
        namespace_query = {'type': type_}

    def transform(cursor):
        if type_ != 'obs':
                return {row.get('uniqueIds')[0]: row.get('uniqueIds')[1:] for row in cursor}
        else:
            obs = {}
            for row in cursor:
                if len(row.get('tlpLevels')) > 1:
                    tlps = row.get('tlpLevels')
                    map_tlps = {}
                    for tlp in tlps:
                        if HASH_MAP.get(tlp):
                            map_tlps[tlp] = HASH_MAP.get(tlp)
                    tlp_level = sorted(map_tlps.items(), key=operator.itemgetter(1))[0][0]
                    id_ = match_tlp_hash(row.get('_id'), tlp_level).get('_id')
                    ids = row.get('uniqueIds')
                    ids.pop(ids.index(id_))
                    obs[id_] = ids
                else:
                    obs[row.get('uniqueIds')[0]] = row.get('uniqueIds')[1:]
            return obs

    return transform(get_db().stix.aggregate([
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
    ], cursor={}))

def match_tlp_hash(hash_, tlp_level):
        def transform(doc):
            return {'_id': doc['_id']}

        return transform(get_db().stix.find_one({
            'data.hash': hash_,
            'data.etlp': tlp_level
        }))
