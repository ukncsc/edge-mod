#!/usr/bin/env python2.7

import os
import sys
import subprocess
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings
if not hasattr(settings, 'BASE_DIR'):
    raise Exception("Failed to import Django settings")
from celery import Celery
app = Celery('caches', config_source='repository.celeryconfig')
from edge import LOCAL_ALIAS
from edge.tools import FileLockOrFail, CannotLock
from crashlog import models as crashlog
from mongoengine.connection import get_db


LOCAL_ALIAS_REGEX = '^%s:' % LOCAL_ALIAS
LOCKNAME = os.path.join(settings.LOCK_DIR, 'dedup_job.lock')


def find_duplicates(db, type_):
    return db.stix.aggregate([
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
        }
    ])


def deduplicate(master, dups):
    print "%s: %s" % (master, dups)
    # TODO: the actual de-duplication - can we use edge/remap or edge/inbox::user_reuser ?


@app.task(ignore_result=True, queue='mapreduce')
def update(force_start=False):
    try:
        with FileLockOrFail(LOCKNAME):
            return update_main(force_start)
    except CannotLock:
        return 0


def update_main(force_start=False):
    try:
        duplicates = find_duplicates(get_db(), 'obs')
        for duplicate in duplicates.get('result'):
            unique_ids = duplicate.get('uniqueIds')
            deduplicate(unique_ids[0], unique_ids[1:])
    except subprocess.CalledProcessError as e:
        crash_message = '\n'.join([
            'returncode=%d' % e.returncode,
            'output:\n%s' % e.output
        ])
        crashlog.save('dedup_job', 'CalledProcessError', crash_message)
        raise

    return 0


def main():
    rc = update()
    sys.exit(rc)


if __name__ == '__main__':
    main()
