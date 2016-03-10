from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from adapters.certuk_mod.config.cert_config import get  as get_config
from adapters.certuk_mod.config.cert_config import save as save_config
from users.decorators import json_body, superuser_or_staff_role


@login_required
@superuser_or_staff_role
@json_body
def ajax_get_crm_url(request, data):
    try:
        url = get_config()
        return JsonResponse({
            'message': "success",
            'config': url
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required
@superuser_or_staff_role
@json_body
def ajax_set_crm_url(request, data):
    try:
        save_config(data)
        return JsonResponse({
            'message': "success",
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)
