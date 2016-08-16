import os
import sys
from dateutil.parser import parse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings

if not hasattr(settings, 'BASE_DIR'): raise Exception('could not load settings.py')
import adapters.certuk_mod.builder.customizations as cert_builder

from edge.generic import EdgeObject
from mongoengine.connection import get_db
from pprint import pprint
from pymongo.errors import BulkWriteError, PyMongoError


def rehash(timestamp):
    """
    A script to recalculate all observable data hashes according to CERT requirements (can safely be run multiple times)
    """
    PAGE_SIZE = 5000
    cert_builder.apply_customizations()
    db = get_db()
    base_query = {
        'type': 'obs',
        'data.summary.type': {
            '$ne': 'ObservableComposition'
        }
    }

    if timestamp:
        base_query.update({'created_on': {
            '$gte': timestamp
        }})

    cursor = db.stix.find(base_query, {'_id': 1})

    bulk = db.stix.initialize_unordered_bulk_op()

    update_count = 0

    for row in cursor:
        update_count += 1
        stix_id = row['_id']
        eo = EdgeObject.load(stix_id)
        ao = eo.to_ApiObject()
        new_hash = ao.localhash()

        bulk.find({
            '_id': stix_id,
            'data.hash': {'$ne': new_hash}
        }).update({
            '$set': {
                'data.hash': new_hash
            }
        })

        if not update_count % PAGE_SIZE:
            bulk.execute()
            bulk = db.stix.initialize_unordered_bulk_op()

    if update_count % PAGE_SIZE:
        bulk.execute()


if __name__ == '__main__':
    timestamp = None
    args = sys.argv
    if len(args) == 2:
        try:
            timestamp = parse(args[1])
        except Exception as e:
            raise e
    rehash(timestamp)
