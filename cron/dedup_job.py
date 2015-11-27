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
from edge.tools import FileLockOrFail, CannotLock
from crashlog import models as crashlog


LOCKNAME = os.path.join(settings.LOCK_DIR, 'dedup_job.lock')


@app.task(ignore_result=True, queue='mapreduce')
def update(force_start=False):
    try:
        with FileLockOrFail(LOCKNAME):
            return update_main(force_start)
    except CannotLock:
        return 0


def update_main(force_start=False):
    js_pathname = os.path.join(settings.BASE_DIR, 'adapters/certuk_mod/cron/dedup_job.js')
    try:
        proc = subprocess.check_output([settings.MONGO_EXE, '--quiet', 'inbox', js_pathname])
    except subprocess.CalledProcessError as e:
        crash_message = '\n'.join([
            'returncode=%d' % e.returncode,
            'output:\n%s' % e.output
        ])
        crashlog.save('dedup_job', 'CalledProcessError', crash_message)
        raise

    print proc
    return 0


def main():
    rc = update()
    sys.exit(rc)


if __name__ == '__main__':
    main()
