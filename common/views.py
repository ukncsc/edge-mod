from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from adapters.certuk_mod.common.activity import find


@login_required
def activity_log(request):
    request.breadcrumbs([("Activity Log", "")])
    return render(request, "activity_log.html", {})


@csrf_exempt
def ajax_activity_log(request, user=None, category=None, state=None, message=None, limit=None):
    try:
        matches = find(user=user, category=category, state=state, message=message, limit=limit)
        return JsonResponse({
            'matches': matches
        }, status=200)
    except Exception as e:
        print e
        return JsonResponse(e, status=500)
