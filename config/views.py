from django.http import JsonResponse
import json

from adapters.certuk_mod.config.cert_config import get as get_config
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
def ajax_set_crm_config(request):
    config = json.loads(request.body)
    config["name"] = "crm_config"
    try:
        save_config("crm_config", config)
        return JsonResponse({}, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_get_crm_config(request):
    try:
        config = get_config("crm_config")
        return JsonResponse(config, safe=False, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_get_sharing_groups(request):
    try:
        sharing_groups = get_config("sharing_groups")
        return JsonResponse(sharing_groups, safe=False, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_set_sharing_groups(request):
    sharing_groups = json.loads(request.body)
    sharing_groups["name"] = "sharing_groups"
    try:
        save_config("sharing_groups", sharing_groups)
        return JsonResponse({}, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_get_markings(request):
    try:
        markings = get_config("markings")
        return JsonResponse(markings, safe=False, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
@superuser_or_staff_role
def ajax_set_markings(request):
    markings = json.loads(request.body)
    markings["name"] = "markings"
    try:
        save_config("markings", markings)
        return JsonResponse({}, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


