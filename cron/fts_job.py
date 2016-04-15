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
from adapters.certuk_mod.fts.config import FtsConfiguration
from adapters.certuk_mod.fts.fts import STIXFts

import traceback


LOCKNAME = os.path.join(settings.LOCK_DIR, 'fts_job.lock')


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
        stix_fts = STIXFts(FtsConfiguration.get())
        stix_fts.run()
    except Exception as e:
        crashlog.save('fts_job', e.message, traceback.format_exc())
        raise

    return 0


def main():
    rtn = update()
    sys.exit(rtn)


if __name__ == '__main__':
    main()
