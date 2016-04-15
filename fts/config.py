from repository.scheduler import PeriodicTaskWithTTL
from mongoengine import DoesNotExist
from adapters.certuk_mod.common.logger import log_error


class FtsConfigurationError(Exception):
    def __init__(self, messages):
        message = '. '.join(messages) + '.'
        super(FtsConfigurationError, self).__init__(message)


class FtsConfiguration(object):
    TASK_NAME = 'adapters.certuk_mod.cron.fts_job.update'
    DEFAULT_HOUR = '00'
    DEFAULT_MINUTE = '00'
    DEFAULT_TIME = DEFAULT_HOUR + ':' + DEFAULT_MINUTE
    DEFAULT_ENABLED = False
    DEFAULT_FULLBUILD = False

    __time_key = 'time'
    __enabled_key = 'enabled'
    __full_build_key = 'full_build'

    def __init__(self, task):
        if not isinstance(task, PeriodicTaskWithTTL):
            raise TypeError('The task must be of type PeriodicTaskWithTTL')

        self.task = task

        errors = FtsConfiguration.__validate(task.crontab.hour, task.crontab.minute)
        if errors:
            raise FtsConfigurationError(errors)

        full_build = task.kwargs.get(self.__full_build_key, self.DEFAULT_FULLBUILD)
        self.hour = task.crontab.hour
        self.minute = task.crontab.minute
        self.enabled = task.enabled
        self.full_build = full_build

    @staticmethod
    def __validate(hour_str, minute_str):
        errors = []
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
            self.__full_build_key: self.full_build,
            self.__time_key: '%02d:%02d' % (int(self.hour), int(self.minute)),
            self.__enabled_key: self.enabled
        }

    @classmethod
    def get(cls):
        try:
            task = PeriodicTaskWithTTL.objects.get(task=cls.TASK_NAME)
            return cls(task)
        except DoesNotExist, e:
            log_error(e, 'adapters/fts/config', 'Configuration for fts task not found')
            raise

    @classmethod
    def set(cls, full_build, time, enabled):
        try:
            config = cls.get()
            task = config.task
        except (DoesNotExist, FtsConfigurationError):
            # Either task has not been saved, or dodgy data was in the database
            task = PeriodicTaskWithTTL(
                    task=cls.TASK_NAME,
                    name='fts',
                    crontab=PeriodicTaskWithTTL.Crontab(month_of_year='*', day_of_month='*', day_of_week='*',
                                                        hour=cls.DEFAULT_HOUR, minute=cls.DEFAULT_MINUTE),
                    enabled=enabled
            )
        task.kwargs = {
            cls.__full_build_key: full_build
        }
        task.enabled = bool(enabled)

        errors = []
        try:
            task.crontab.hour = time.split(':')[0]
            task.crontab.minute = time.split(':')[1]
        except IndexError:
            errors.append("Invalid time")

        errors += FtsConfiguration.__validate(task.crontab.hour, task.crontab.minute)

        if errors:
            raise FtsConfigurationError(errors)

        task.save()
        return cls.get()

    @classmethod
    def set_from_dict(cls, config_dict):
        return cls.set(config_dict[cls.__full_build_key],
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
        return cls.set(FtsConfiguration.DEFAULT_FULLBUILD,
                       FtsConfiguration.DEFAULT_TIME,
                       FtsConfiguration.DEFAULT_ENABLED)
