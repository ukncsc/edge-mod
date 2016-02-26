import re
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
def ajax_activity_log(request, search):
    try:
        pattern = re.compile(
            r'((?:cat|regex|state|user):\S+)',
            flags=re.IGNORECASE
        )
        match = pattern.findall(search)
        if match:
            find_params = {k: v for k, v in (x.split(':') for x in match)}
            matches = find(
                category=find_params.get('cat', None),
                regex=find_params.get('regex', None),
                state=find_params.get('state', None),
                user=find_params.get('user', None)
            )
        else:
            matches = find(regex=search)
        return JsonResponse({
            'matches': matches
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)
