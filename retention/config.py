from repository.scheduler import PeriodicTaskWithTTL
from mongoengine import DoesNotExist
from adapters.certuk_mod.common.logger import log_error


class RetentionConfigurationError(Exception):
    def __init__(self, messages):
        message = '. '.join(messages) + '.'
        super(RetentionConfigurationError, self).__init__(message)


class RetentionConfiguration(object):
    TASK_NAME = 'adapters.certuk_mod.cron.purge_job.update'
    DEFAULT_MAX_AGE_IN_MONTHS = 36
    DEFAULT_MIN_SIGHTINGS = 2
    DEFAULT_MIN_BACK_LINKS = 1
    DEFAULT_LOCAL_NS = True
    DEFAULT_HOUR = '00'
    DEFAULT_MINUTE = '00'
    DEFAULT_TIME = DEFAULT_HOUR + ':' + DEFAULT_MINUTE
    DEFAULT_ENABLED = False

    __max_age_key = 'max_age_in_months'
    __min_sightings_key = 'minimum_sightings'
    __min_back_links_key = 'minimum_back_links'
    __local_ns_key = 'localNamespaceOnly'
    __time_key = 'time'
    __enabled_key = 'enabled'

    def __init__(self, task):
        if not isinstance(task, PeriodicTaskWithTTL):
            raise TypeError('The task must be of type PeriodicTaskWithTTL')

        self.task = task

        max_age_in_months = task.kwargs.get(self.__max_age_key, self.DEFAULT_MAX_AGE_IN_MONTHS)
        minimum_sightings = task.kwargs.get(self.__min_sightings_key, self.DEFAULT_MIN_SIGHTINGS)
        minimum_back_links = task.kwargs.get(self.__min_back_links_key, self.DEFAULT_MIN_BACK_LINKS)
        only_local_ns = task.kwargs.get(self.__local_ns_key, self.DEFAULT_LOCAL_NS)

        errors = RetentionConfiguration.__validate(max_age_in_months, minimum_sightings, minimum_back_links,
                                                   only_local_ns, task.crontab.hour, task.crontab.minute)
        if errors:
            raise RetentionConfigurationError(errors)

        self.max_age_in_months = max_age_in_months
        self.minimum_sightings = minimum_sightings
        self.minimum_back_links = minimum_back_links
        self.only_local_ns = only_local_ns
        self.hour = task.crontab.hour
        self.minute = task.crontab.minute
        self.enabled = task.enabled

    @staticmethod
    def __validate(max_age_in_months, minimum_sightings, minimum_back_links, only_local_ns, hour_str, minute_str):
        errors = []
        if not isinstance(max_age_in_months, int):
            errors.append('Integer required for max_age_in_months')
        if max_age_in_months < 0:
            errors.append('max_age_in_months must be greater than 0')

        if not isinstance(minimum_sightings, int):
            errors.append('Integer required for minimum_sightings')
        if minimum_sightings < 2:
            errors.append('minimum_sightings must be greater than 1')

        if not isinstance(minimum_back_links, int):
            errors.append('Integer required for minimum_back_links')
        if minimum_back_links < 1:
            errors.append('minimum_back_links must be greater than 1')

        if not isinstance(only_local_ns, bool):
            errors.append('Boolean required for only_local_ns')

        try:
            hour = int(hour_str)
            minute = int(minute_str)
        except ValueError:
            errors.append("Invalid time")
        else:
            if not 0 <= hour < 24 or not 0 <= minute < 60:
                errors.append("Time outside valid range")

        return errors

    def to_dict(self):
        return {
            self.__max_age_key: self.max_age_in_months,
            self.__min_sightings_key: self.minimum_sightings,
            self.__min_back_links_key: self.minimum_back_links,
            self.__local_ns_key: self.only_local_ns,
            self.__time_key: '%02d:%02d' % (int(self.hour), int(self.minute)),
            self.__enabled_key: self.enabled
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
    def set(cls, max_age_in_months, minimum_sightings, minimum_back_links, only_local_ns, time, enabled):
        try:
            config = cls.get()
            task = config.task
        except (DoesNotExist, RetentionConfigurationError):
            # Either task has not been saved, or dodgy data was in the database
            task = PeriodicTaskWithTTL(
                task=cls.TASK_NAME,
                name='purge',
                crontab=PeriodicTaskWithTTL.Crontab(month_of_year='*', day_of_month='*', day_of_week='*',
                                                    hour=cls.DEFAULT_HOUR, minute=cls.DEFAULT_MINUTE),
                enabled=enabled
            )
        task.kwargs = {
            cls.__max_age_key: max_age_in_months,
            cls.__min_sightings_key: minimum_sightings,
            cls.__min_back_links_key: minimum_back_links,
            cls.__local_ns_key: only_local_ns
        }
        task.enabled = bool(enabled)

        errors = []
        try:
            task.crontab.hour = time.split(':')[0]
            task.crontab.minute = time.split(':')[1]
        except IndexError:
            errors.append("Invalid time")

        errors += RetentionConfiguration.__validate(max_age_in_months, minimum_sightings, minimum_back_links,
                                                    only_local_ns, task.crontab.hour, task.crontab.minute)

        if errors:
            raise RetentionConfigurationError(errors)

        task.save()
        return cls.get()

    @classmethod
    def set_from_dict(cls, config_dict):
        return cls.set(config_dict[cls.__max_age_key], config_dict[cls.__min_sightings_key],
                       config_dict[cls.__min_back_links_key], config_dict[cls.__local_ns_key],
                       config_dict[cls.__time_key],
                       config_dict[cls.__enabled_key])

    @classmethod
    def install(cls):
        try:
            return cls.get()
        except DoesNotExist:
            return cls.reset()

    @classmethod
    def reset(cls):
        return cls.set(RetentionConfiguration.DEFAULT_MAX_AGE_IN_MONTHS,
                       RetentionConfiguration.DEFAULT_MIN_SIGHTINGS,
                       RetentionConfiguration.DEFAULT_MIN_BACK_LINKS,
                       RetentionConfiguration.DEFAULT_LOCAL_NS,
                       RetentionConfiguration.DEFAULT_TIME,
                       RetentionConfiguration.DEFAULT_ENABLED)
