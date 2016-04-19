import os
from django.conf import settings
from mongoengine.connection import get_db
from edge.tools import StopWatch
from search.mongofts import document_prose, FTS_KEY
from adapters.certuk_mod.common.activity import save as log_activity

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')

if not hasattr(settings, 'BASE_DIR'): raise Exception('could not load settings.py')


class STIXFts(object):
    PAGE_SIZE = 20

    def __init__(self, fts_config):
        self.fts_config = fts_config

    def run(self):
        db = get_db()
        update_timer = StopWatch()
        query = {}
        if not self.fts_config.full_build:
            query['fts'] = {"$eq": None}

        bulk_op = db.stix.initialize_unordered_bulk_op()
        update_count = 0
        for doc in db.stix.find(query):
            fts_data = document_prose(doc)

            if 'fts' in doc and fts_data[FTS_KEY] == doc['fts']:
                continue

            update_count += 1
            bulk_op.find({'_id': doc['_id']}).update({'$set': fts_data})
            if not update_count % STIXFts.PAGE_SIZE:
                bulk_op.execute()
                bulk_op = db.stix.initialize_unordered_bulk_op()

        if update_count % STIXFts.PAGE_SIZE:
            bulk_op.execute()

        log_activity("system", 'FTS', 'INFO',
                     "%s : Updated %d of %d objects in %dms" %
                     (
                         'Full Rebuild' if self.fts_config.full_build else 'Missing FTS Insert',
                         update_count,
                         db.stix.count(),
                         update_timer.ms())
                     )
