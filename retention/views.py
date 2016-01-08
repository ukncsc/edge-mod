
from django.contrib.auth.decorators import login_required
from users.decorators import json_body, superuser_or_staff_role
from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.retention.config import RetentionConfiguration


@login_required
@superuser_or_staff_role
@json_body
def ajax_get_retention_config(request, data):
    success = True
    error_message = ""
    config_values = {}

    try:
        ret_config = RetentionConfiguration.get()
        config_values = ret_config.to_dict()
    except Exception, e:
        success = False
        error_message = e.message
        log_error(e, 'Retention config')

    response = {
        'success': success,
        'error_message': error_message
    }
    response.update(config_values)

    return response


@login_required
@superuser_or_staff_role
@json_body
def ajax_set_retention_config(request, data):
    success = True
    error_message = ""

    try:
        RetentionConfiguration.set_from_dict(data)
    except Exception, e:
        success = False
        if isinstance(e, KeyError):
            error_message = 'value missing: %s' % e.message
        else:
            error_message = e.message
        log_error(e, 'Retention config')

    return {
        'success': success,
        'error_message': error_message
    }


@login_required
@superuser_or_staff_role
@json_body
def ajax_reset_retention_config(request, data):
    success = True
    error_message = ""
    config_values = {}

    try:
        RetentionConfiguration.reset()
        ret_config = RetentionConfiguration.get()
        config_values = ret_config.to_dict()
    except Exception, e:
        success = False
        log_error(e, 'Retention config')

    response = {
        'success': success,
        'error_message': error_message
    }
    response.update(config_values)

    return response
