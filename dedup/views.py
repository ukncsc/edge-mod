import json
import datetime

from defusedxml import EntitiesForbidden
from users.decorators import json_body, superuser_or_staff_role
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lxml.etree import XMLSyntaxError
from mongoengine import DoesNotExist

from adapters.certuk_mod.common.activity import save as log_activity
from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from adapters.certuk_mod.dedup.dedup import STIXDedup
from adapters.certuk_mod.dedup.config import DedupConfiguration
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from edge.inbox import InboxError
from edge.tools import StopWatch
from users.decorators import login_required_ajax, superuser_role
from users.models import Repository_User
from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES


@login_required
@superuser_role
def duplicates_finder(request):
    request.breadcrumbs([("Duplicates Finder", "")])
    return render(request, "duplicates_finder.html", {
        "kill_chain_phases": {item['phase_id']: item['name'] for item in KILL_CHAIN_PHASES
                              }})


@login_required_ajax
@superuser_role
def ajax_load_duplicates(request, typ):
    try:
        local = request.body
        duplicates = STIXDedup.find_duplicates(local)
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
        "package": package.to_dict(),
        "type_info" : [{"id_": id_, "ty":root_edge_object.ty}]
    }, status=200)


@login_required_ajax
def ajax_load_parent_ids(request):
    result = {}
    try:
        raw_body = json.loads(request.body)
        original, duplicate = raw_body.get('original'), raw_body.get('duplicate')
        parents_of_original, parents_of_duplicate = STIXDedup.calculate_backlinks(original, duplicate)
        for _id in parents_of_original.keys():
            result.setdefault('original', []).append(_id)
        for _id in parents_of_duplicate.keys():
            result.setdefault('duplicate', []).append(_id)
        return JsonResponse(result, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)

def build_activity_message(count, duration, messages, validation_result):
    validation_text = []
    if validation_result:
        for id_, fields in validation_result.iteritems():
            validation_text.append('%s:' % id_)
            for field_id, validation in fields.iteritems():
                validation_text.append('\t%5s: %s - %s' % (validation['status'], field_id, validation['message']))
        if len(validation_text) > 0:
            validation_text.insert(0, '\nValidation:')

    return 'Ingested %d objects in %dms\nMessages:\n\t%s%s' % (
        count,
        duration,
        '\n\t'.join(messages),
        '\n\t'.join(validation_text)
    )


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
        duration = int(elapsed.ms())
        if len(ip.filter_messages) == 0 and ip.message:
            ip.filter_messages.append(ip.message)
        log_activity(username, 'DEDUP', 'INFO', build_activity_message(
            ip.saved_count, duration, ip.filter_messages, ip.validation_result
        ))
        return JsonResponse({
            'count': ip.saved_count,
            'duration': duration,
            'messages': ip.filter_messages,
            'state': 'success',
            'validation_result': ip.validation_result
        }, status=202)
    except (XMLSyntaxError, EntitiesForbidden, InboxError) as e:
        count = ip.saved_count if isinstance(ip, DedupInboxProcessor) else 0
        duration = int(elapsed.ms())
        messages = [e.message]
        validation_result = ip.validation_result if isinstance(ip, DedupInboxProcessor) else {}
        log_activity(username, 'DEDUP', 'WARN', build_activity_message(
            count, duration, messages, validation_result
        ))
        return JsonResponse({
            'count': count,
            'duration': duration,
            'messages': messages,
            'state': 'invalid',
            'validation_result': validation_result
        }, status=400)
    except Exception as e:
        log_activity(username, 'DEDUP', 'ERROR', e.message)
        log_error(e, 'adapters/dedup/import', 'Import failed')
        return JsonResponse({
            'duration': int(elapsed.ms()),
            'messages': [e.message],
            'state': 'error'
        }, status=500)


@login_required
@superuser_or_staff_role
@json_body
def ajax_get_dedup_config(request, data):
    success = True
    error_message = ""
    config_values = {}

    try:
        dedup_config = DedupConfiguration.get()
        config_values = dedup_config.to_dict()
    except Exception, e:
        success = False
        error_message = e.message
        log_error(e, 'DEDUP config')

    response = {
        'success': success,
        'error_message': error_message
    }
    response.update(config_values)

    return response


@login_required
@superuser_or_staff_role
@json_body
def ajax_set_dedup_config(request, data):
    success = True
    error_message = ""

    try:
        DedupConfiguration.set_from_dict(data)
    except Exception, e:
        success = False
        if isinstance(e, KeyError):
            error_message = 'value missing: %s' % e.message
        else:
            error_message = e.message
        log_error(e, 'DEDUP config')

    return {
        'success': success,
        'error_message': error_message
    }


@login_required
@superuser_or_staff_role
@json_body
def ajax_reset_dedup_config(request, data):
    success = True
    error_message = ""
    config_values = {}

    try:
        DedupConfiguration.reset()
        dedup_config = DedupConfiguration.get()
        config_values = dedup_config.to_dict()
    except Exception, e:
        success = False
        log_error(e, 'Fts config')

    response = {
        'success': success,
        'error_message': error_message
    }
    response.update(config_values)

    return response
