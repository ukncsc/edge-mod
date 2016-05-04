import datetime
from dateutil import parser as dt_parser

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from edge.generic import EdgeObject, EdgeError
from users.decorators import login_required_ajax

from adapters.certuk_mod.common.objectid import discover as objectid_discover
from adapters.certuk_mod.common.views import error_with_message
from adapters.certuk_mod.patch.incident_patch import PRETTY_TIME_TYPE


def unix_time_millis(dt):
    naive = dt.replace(tzinfo=None)
    return (naive - datetime.datetime(1970, 1, 1)).total_seconds() * 1000.0


def get_local_datetime(time_str):
    dt_in = dt_parser.parse(time_str)
    return dt_in if not dt_in.tzinfo else dt_in.astimezone(settings.LOCAL_TZ)


@login_required
def timeline_discover(request):
    return objectid_discover(request,
                             "incident_timeline",
                             "incident_timeline_not_found")


@login_required
def incident_timeline(request, id_):
    request.breadcrumbs([("Timeline", "")])
    return render(request, "incident_timeline.html", {
        "stix_id": id_
    })


@login_required
def incident_timeline_not_found(request):
    return error_with_message(request,
                              "No incident object found")


@login_required_ajax
def ajax_incident_timeline(request, id_):
    try:
        edge_object = EdgeObject.load(id_)
    except EdgeError as e:
        return JsonResponse(dict(e), status=400)

    try:
        if edge_object.ty != 'inc':
            return JsonResponse({'message': "Only timelines for Incidents can be viewed"}, status=400)

        time_dict = edge_object.obj.time.to_dict()
        graph = dict()
        graph['nodes'] = []
        graph['links'] = []
        graph['title'] = "Incident : " + edge_object.obj.title
        graph['tzname'] = datetime.datetime.now(settings.LOCAL_TZ).tzname()

        for key, value in time_dict.iteritems():
            if isinstance(value, basestring):
                time_ms = unix_time_millis(get_local_datetime(time_dict[key]))
            else:  # stored in value field
                time_ms = unix_time_millis(get_local_datetime(time_dict[key]['value']))

            graph['nodes'].append({"name": PRETTY_TIME_TYPE[key], "date": time_ms})

        return JsonResponse(graph, status=200)

    except Exception as e:
        ext_ref_error = "not found"
        if e.message.endswith(ext_ref_error):
            JsonResponse({'message': "Unable to load object as some external " \
                                     "references were not found: " + e.message[0:-len(ext_ref_error)]})
        else:
            return JsonResponse(dict(e), status=500)
