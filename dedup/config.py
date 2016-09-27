from repository.scheduler import PeriodicTaskWithTTL
from mongoengine.errors import DoesNotExist
from adapters.certuk_mod.common.logger import log_error


class DedupConfigurationError(Exception):
    def __init__(self, messages):
        message = '. '.join(messages) + '.'
        super(DedupConfigurationError, self).__init__(message)


class DedupConfiguration(object):

    TASK_NAME = 'adapters.certuk_mod.cron.dedup_job.update'
    DEFAULT_LOCAL_NS = True
    DEFAULT_HOUR = '00'
    DEFAULT_MINUTE = '00'
    DEFAULT_TIME = DEFAULT_HOUR + ':' + DEFAULT_MINUTE
    DEFAULT_ENABLED = False

    __time_key = 'time'
    __enabled_key = 'enabled'
    __local_ns_key = 'localNamespaceOnly'

    def __init__(self, task):
        if not isinstance(task, PeriodicTaskWithTTL):
            raise TypeError('The task must be of type PeriodicTaskWithTTL')

        self.task = task

        only_local_ns = task.kwargs.get(self.__local_ns_key, self.DEFAULT_LOCAL_NS)

        errors = DedupConfiguration.__validate(only_local_ns, task.crontab.hour, task.crontab.minute)
        if errors:
            raise DedupConfigurationError(errors)

        self.only_local_ns = only_local_ns
        self.hour = task.crontab.hour
        self.minute = task.crontab.minute
        self.enabled = task.enabled
        # self.object_types = task.args

    @staticmethod
    def __validate(only_local_ns, hour_str, minute_str):
        errors = []

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
            log_error(e, 'adapters/dedup/config', 'Configuration for dedup task not found')
            raise

    @classmethod
    def set(cls, only_local_ns, time, enabled):
        try:
            config = cls.get()
            task = config.task
        except (DoesNotExist, DedupConfigurationError):
            # Either task has not been saved, or dodgy data was in the database
            task = PeriodicTaskWithTTL(
                task=cls.TASK_NAME,
                name='dedup',
                crontab=PeriodicTaskWithTTL.Crontab(month_of_year='*', day_of_month='*', day_of_week='*',
                                                    hour=cls.DEFAULT_HOUR, minute=cls.DEFAULT_MINUTE),
                enabled=enabled
            )

        task.kwargs = {
            cls.__local_ns_key: only_local_ns
        }

        task.enabled = bool(enabled)

        errors = []
        try:
            task.crontab.hour = time.split(':')[0]
            task.crontab.minute = time.split(':')[1]
        except IndexError:
            errors.append("Invalid time")

        errors += DedupConfiguration.__validate(only_local_ns, task.crontab.hour, task.crontab.minute)

        if errors:
            raise DedupConfigurationError(errors)

        task.save()
        return cls.get()

    @classmethod
    def set_from_dict(cls, config_dict):
        return cls.set(config_dict[cls.__local_ns_key],
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
        return cls.set(DedupConfiguration.DEFAULT_LOCAL_NS,
                       DedupConfiguration.DEFAULT_TIME,
                       DedupConfiguration.DEFAULT_ENABLED)
