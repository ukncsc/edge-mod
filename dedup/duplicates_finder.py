import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings

if not hasattr(settings, 'BASE_DIR'):
    raise Exception("Failed to import Django settings")
from edge import LOCAL_ALIAS
from mongoengine.connection import get_db

LOCAL_ALIAS_REGEX = '^%s:' % LOCAL_ALIAS


def find_duplicates(type_):
    def transform(cursor):
        return [{'original': row.get('uniqueIds')[0], 'duplicates': row.get('uniqueIds')[1:]} for row in cursor]

    return transform(get_db().stix.aggregate([
        {
            '$match': {
                '_id': {
                    '$regex': LOCAL_ALIAS_REGEX
                },
                'type': type_
            }
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
