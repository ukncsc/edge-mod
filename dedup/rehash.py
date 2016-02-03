import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings
if not hasattr(settings, 'BASE_DIR'): raise Exception('could not load settings.py')
import adapters.certuk_mod.builder.customizations as cert_builder
from edge.generic import EdgeObject
from mongoengine.connection import get_db
from pprint import pprint
from pymongo.errors import BulkWriteError, PyMongoError


def main():
    """
    A script to recalculate all observable data hashes according to CERT requirements (can safely be run multiple times)
    """
    cert_builder.apply_customizations()

    db = get_db()
    cursor = db.stix.find({
        'type': 'obs',
        'data.api.observable_composition': None
    }, {
        '_id': 1
    })

    bulk = db.stix.initialize_unordered_bulk_op()

    for row in cursor:
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

    try:
        bulk_result = bulk.execute()
    except PyMongoError as pme:
        print pme
    except BulkWriteError as bwe:
        pprint(bwe.details)
    else:
        pprint(bulk_result)


if __name__ == '__main__':
    main()
