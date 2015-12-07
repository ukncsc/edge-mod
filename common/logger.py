
from crashlog import models as crash_log
import traceback


def log_error(e, app_name, message=''):
    stack_trace = traceback.format_exc()
    crash_log.save(app_name, message + ': ' + str(e), stack_trace)
