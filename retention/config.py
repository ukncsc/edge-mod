
from repository.scheduler import PeriodicTaskWithTTL
from mongoengine import DoesNotExist
from adapters.certuk_mod.common.logger import log_error


class RetentionConfiguration(object):

    TASK_NAME = 'adapters.certuk_mod.cron.purge_job.update'
    DEFAULT_MAX_AGE_IN_MONTHS = 36
    DEFAULT_MIN_SIGHTINGS = 2

    __max_age_key = 'max_age_in_months'
    __min_sightings_key = 'minimum_sightings'

    def __init__(self, task):
        if not isinstance(task, PeriodicTaskWithTTL):
            raise TypeError('The task must be of type PeriodicTaskWithTTL')

        self.task = task

        max_age_in_months = task.kwargs[self.__max_age_key]
        minimum_sightings = task.kwargs[self.__min_sightings_key]

        if not isinstance(max_age_in_months, int):
            raise TypeError('Integer required for max_age_in_months')
        if max_age_in_months < 0:
            raise ValueError('max_age_in_months must be greater than 0')
        self.max_age_in_months = max_age_in_months

        if not isinstance(minimum_sightings, int):
            raise TypeError('Integer required for minimum_sightings')
        if minimum_sightings < 2:
            raise ValueError('minimum_sightings must be greater than 1')
        self.minimum_sightings = minimum_sightings

    def to_dict(self):
        return {
            self.__max_age_key: self.max_age_in_months,
            self.__min_sightings_key: self.minimum_sightings
        }

    @classmethod
    def get(cls):
        try:
            task = PeriodicTaskWithTTL.objects.get(task=cls.TASK_NAME)
            return cls(task)
        except DoesNotExist, e:
            log_error(e, 'adapters/retention/config', 'Configuration for retention task not found')
            raise

    @classmethod
    def set(cls, max_age_in_months, minimum_sightings):
        try:
            config = cls.get()
            task = config.task
        except DoesNotExist:
            task = PeriodicTaskWithTTL(
                task=cls.TASK_NAME,
                name='purge',
                crontab=PeriodicTaskWithTTL.Crontab(month_of_year='*', day_of_month='*', day_of_week='*', hour='0',
                                                    minute='*'),
                enabled=True
            )
        task.kwargs = {
            cls.__max_age_key: max_age_in_months,
            cls.__min_sightings_key: minimum_sightings
        }
        task.save()

    @classmethod
    def set_from_dict(cls, config_dict):
        cls.set(config_dict[cls.__max_age_key], config_dict[cls.__min_sightings_key])

    @staticmethod
    def install():
        return RetentionConfiguration.set(RetentionConfiguration.DEFAULT_MAX_AGE_IN_MONTHS,
                                          RetentionConfiguration.DEFAULT_MIN_SIGHTINGS)
