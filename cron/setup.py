
from repository.scheduler import PeriodicTaskWithTTL
from mongoengine import DoesNotExist


tasks = (
    {'name': 'purge', 'task': 'adapters.certuk_mod.cron.purge_job.update', 'hour': '0'},
    # {'name': 'dedup', 'task': 'adapters.certuk_mod.cron.dedup_job.update', 'interval': 15}
)


def create_jobs():
    for item in tasks:
        try:
            PeriodicTaskWithTTL.objects.get(name=item['name'])
        except DoesNotExist:
            PeriodicTaskWithTTL(
                task=item['task'],
                name=item['name'],
                crontab=PeriodicTaskWithTTL.Crontab(month_of_year='*', day_of_month='*', day_of_week='*',
                                                    hour=item['hour'], minute='*'),
                enabled=True
            ).save()
