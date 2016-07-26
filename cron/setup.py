
from adapters.certuk_mod.retention.config import RetentionConfiguration
from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.fts.config import FtsConfiguration
from adapters.certuk_mod.dedup.config import DedupConfiguration


tasks = (
    {
        'name': 'fts',
        'task': FtsConfiguration.TASK_NAME,
        'hour': '0',
        'installer': FtsConfiguration.install
    },
    {
        'name': 'purge',
        'task': RetentionConfiguration.TASK_NAME,
        'hour': '0',
        'installer': RetentionConfiguration.install
    },
    {
        'name': 'dedup',
        'task': DedupConfiguration.TASK_NAME,
        'hour': '0',
        'installer': DedupConfiguration.install
    }
)


def create_jobs():
    for item in tasks:
        try:
            item['installer']()
        except Exception, e:
            log_error(e, 'adapters/cron/setup')
