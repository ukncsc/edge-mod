import os
from time import sleep

from celery.exceptions import TimeoutError
from mongoengine.connection import get_db
from datetime import datetime
from dateutil.relativedelta import relativedelta
from repository.scheduler import PeriodicTaskWithTTL

from adapters.certuk_mod.common.activity import save as log_activity

import os
import sys
import argparse
from mongoengine.connection import get_db

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings
if not hasattr(settings, 'BASE_DIR'): raise Exception('could not load settings.py')

from edge.tools import StopWatch, EstimatingStopWatch
from search.mongofts import document_prose


class STIXFts(object):

    PAGE_SIZE = 5000

    def __init__(self, fts_config):
        self.fts_config = fts_config

    def run(self):
        self.stderr('Rebuilding FTS, Full build:' + str(self.fts_config.full_build))
        db = get_db()
        total_documents = db.stix.count()
        scanned = 0

        progress = lambda: 'generating text: [% 8d / % 8d]' % (scanned, total_documents)
        total_timer = EstimatingStopWatch(total_documents)
        update_timer = StopWatch()
        for doc in db.stix.find():
            scanned += 1
            if not self.fts_config.full_build and doc['fts']:
                continue

            fts_data = document_prose(doc)

            if not fts_data['fts'] and not doc['fts']:
                continue

            db.stix.update({'_id': doc['_id']},
                           {'$set': fts_data})

            if update_timer.ms() > 1000:
                update_timer = StopWatch()
                hh, mm, ss = total_timer.eta_hms(scanned)
                self.stderr(progress() + ' (% 3d:%02d:%02d remaining)\r' % (hh, mm, ss))
        self.stderr(progress() + '\n')

    def stderr(self, value):
        sys.stderr.write(value)
        sys.stderr.flush()
