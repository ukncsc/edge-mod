from defusedxml import EntitiesForbidden
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lxml.etree import XMLSyntaxError
from mongoengine import DoesNotExist

from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from edge.inbox import InboxError
from edge.tools import StopWatch
from users.decorators import login_required_ajax
from users.models import Repository_User
from .duplicates_finder import find_duplicates


@login_required
def duplicates_finder(request):
    request.breadcrumbs([("Duplicates Finder", "")])
    return render(request, "duplicates_finder.html", {})


@login_required_ajax
def ajax_load_duplicates(request, typ):
    try:
        duplicates = find_duplicates(typ)
        return JsonResponse({
            typ: duplicates
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
def ajax_load_object(request, id_):
    root_edge_object = PublisherEdgeObject.load(id_)
    package = PackageGenerator.build_package(root_edge_object)
    return JsonResponse({
        "root_id": id_,
        "package": package.to_dict()
    }, status=200)


@login_required_ajax
def ajax_load_parent_ids(request, id_):
    try:
        parents = {}
        return JsonResponse(parents, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@csrf_exempt
def ajax_import(request, username):
    if not request.method == 'POST':
        return JsonResponse({}, status=405)
    if not request.META.get('HTTP_ACCEPT') == 'application/json':
        return JsonResponse({}, status=406)
    if not request.META.get('CONTENT_TYPE') in {'application/xml', 'text/xml'}:
        return JsonResponse({}, status=415)

    try:
        request.user = Repository_User.objects.get(username=username)
    except DoesNotExist:
        return JsonResponse({}, status=403)

    elapsed = StopWatch()
    ip = None
    try:
        ip = DedupInboxProcessor(user=request.user, streams=[(request, None)])
        ip.run()
        return JsonResponse({
            'count': ip.saved_count,
            'duration': '%.2f' % elapsed.ms(),
            'message': ip.message,
            'state': 'success',
            'validation_result': ip.validation_result
        }, status=202)
    except (XMLSyntaxError, EntitiesForbidden, InboxError) as e:
        return JsonResponse({
            'duration': '%.2f' % elapsed.ms(),
            'message': e.message,
            'state': 'invalid',
            'validation_result': ip.validation_result if isinstance(ip, DedupInboxProcessor) else None
        }, status=400)
    except Exception as e:
        log_error(e, 'adapters/dedup/import', 'Import failed')
        return JsonResponse({
            'duration': '%.2f' % elapsed.ms(),
            'message': e.message,
            'state': 'error'
        }, status=500)
