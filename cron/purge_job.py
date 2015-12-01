#!/usr/bin/env python2.7

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings
if not hasattr(settings, 'BASE_DIR'):
    raise Exception("Failed to import Django settings")

from celery import Celery
app = Celery('certuk', config_source='repository.celeryconfig')

from crashlog import models as crashlog
from edge.tools import FileLockOrFail, CannotLock
from adapters.certuk_mod.retention.config import RetentionConfiguration
from adapters.certuk_mod.retention.purge import STIXPurge

import traceback


LOCKNAME = os.path.join(settings.LOCK_DIR, 'purge_job.lock')


@app.task(name='adapters.certuk_mod.cron.purge_job.update', ignore_result=True, queue='certuk')
def update(force_start=False):
    try:
        with FileLockOrFail(LOCKNAME):
            return update_main(force_start)
    except CannotLock:
        return 0


def update_main(force_start=False):
    try:
        max_age = RetentionConfiguration.get_retention_age_in_months()
        min_sightings = RetentionConfiguration.get_minimum_number_of_sightings()
        stix_purge = STIXPurge(max_age, min_sightings)
        stix_purge.run()
    except Exception as e:
        crashlog.save('purge_job', e.message, traceback.format_exc())
        raise

    return 0


def main():
    rtn = update()
    sys.exit(rtn)


if __name__ == '__main__':
    main()
