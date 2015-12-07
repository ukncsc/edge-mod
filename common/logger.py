
from crashlog import models as crash_log
import traceback
import inspect


def log_error(e, app_name, message=''):
    stack_trace = traceback.format_exc()
    crash_log.save(app_name, message + ': ' + str(e), stack_trace)


def get_exception_stack_variable(variable_name):
    local_vars = inspect.trace()[-1][0].f_locals
    return local_vars.get(variable_name)
