#!/usr/bin/env python2.7
import os
import sys

from crashlog import models as crashlog

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings
if not hasattr(settings, 'BASE_DIR'):
    raise Exception("Failed to import Django settings")

from celery import Celery
app = Celery('certuk', config_source='repository.celeryconfig')

from edge.tools import FileLockOrFail, CannotLock
from adapters.certuk_mod.dedup.config import DedupConfiguration
from adapters.certuk_mod.dedup.dedup import STIXDedup

import traceback

LOCKNAME = os.path.join(settings.LOCK_DIR, 'dedup_job.lock')


@app.task(ignore_result=True, queue='celery')
def update(force_start=False, **kwargs):
    try:
        with FileLockOrFail(LOCKNAME):
            return update_main(force_start, **kwargs)
    except CannotLock:
        return 0


def task_is_running():
    try:
        with FileLockOrFail(LOCKNAME):
            return False
    except CannotLock:
        return True


def update_main(force_start=False, **kwargs):
    try:
        stix_dedup = STIXDedup(DedupConfiguration.get())
        stix_dedup.run()
    except Exception as e:
        crashlog.save('dedup_job', e.message, traceback.format_exc())
        raise

    return 0


def main():
    rtn = update()
    sys.exit(rtn)


if __name__ == '__main__':
    main()
