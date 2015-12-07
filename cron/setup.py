
from adapters.certuk_mod.retention.config import RetentionConfiguration
from adapters.certuk_mod.common.logger import log_error


tasks = (
    {
        'name': 'purge',
        'task': RetentionConfiguration.TASK_NAME,
        'hour': '0',
        'installer': RetentionConfiguration.install
    },
    # {'name': 'dedup', 'task': 'adapters.certuk_mod.cron.dedup_job.update', 'interval': 15}
)


def create_jobs():
    for item in tasks:
        try:
            item['installer']()
        except Exception, e:
            log_error(e, 'adapters/cron/setup')
