from django.http import JsonResponse
import json

from adapters.certuk_mod.config.cert_config import get  as get_config
from adapters.certuk_mod.config.cert_config import save as save_config
from adapters.certuk_mod.config.cert_config import get_all as get_all
from users.decorators import superuser_or_staff_role, login_required_ajax


def ajax_get_cert_config(request):
    try:
        config = get_all()
        return JsonResponse(config, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_get_crm_url(request):
    try:
        url = get_config("crmURL")
        return JsonResponse({
            'crmURL': url
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_get_sharing_groups(request):
    try:
        sharing_groups = get_config("sharing_groups")
        return JsonResponse(sharing_groups, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_set_sharing_groups(request):
    sharing_groups = json.loads(request.body)
    try:
        save_config("sharing_groups", sharing_groups)
        return JsonResponse({}, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_set_crm_url(request):
    url = json.loads(request.body)

    if validate(url):
        try:
            save_config("crmURL", url)
            return JsonResponse({}, status=200)
        except Exception as e:
            return JsonResponse({
                'message': e.message
            }, status=500)
    else:
        return JsonResponse({
            'message': "Invalid URL"
        }, status=400)


def validate(value):
    return value.endswith("crmapi")
