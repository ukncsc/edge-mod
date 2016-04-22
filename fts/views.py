
from django.contrib.auth.decorators import login_required
from users.decorators import json_body, superuser_or_staff_role
from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.fts.config import FtsConfiguration


@login_required
@superuser_or_staff_role
@json_body
def ajax_get_fts_config(request, data):
    success = True
    error_message = ""
    config_values = {}

    try:
        fts_config = FtsConfiguration.get()
        config_values = fts_config.to_dict()
    except Exception, e:
        success = False
        error_message = e.message
        log_error(e, 'FTS config')

    response = {
        'success': success,
        'error_message': error_message
    }
    response.update(config_values)

    return response


@login_required
@superuser_or_staff_role
@json_body
def ajax_set_fts_config(request, data):
    success = True
    error_message = ""

    try:
        FtsConfiguration.set_from_dict(data)
    except Exception, e:
        success = False
        if isinstance(e, KeyError):
            error_message = 'value missing: %s' % e.message
        else:
            error_message = e.message
        log_error(e, 'Fts config')

    return {
        'success': success,
        'error_message': error_message
    }


@login_required
@superuser_or_staff_role
@json_body
def ajax_reset_fts_config(request, data):
    success = True
    error_message = ""
    config_values = {}

    try:
        FtsConfiguration.reset()
        fts_config = FtsConfiguration.get()
        config_values = fts_config.to_dict()
    except Exception, e:
        success = False
        log_error(e, 'Fts config')

    response = {
        'success': success,
        'error_message': error_message
    }
    response.update(config_values)

    return response
