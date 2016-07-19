import json

from defusedxml import EntitiesForbidden
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lxml.etree import XMLSyntaxError
from mongoengine import DoesNotExist
from mongoengine.connection import get_db

from adapters.certuk_mod.common.activity import save as log_activity
from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from edge.inbox import InboxError, InboxProcessorForBuilders, InboxItem
from edge.generic import EdgeObject
from edge.models import StixBacklink
from edge.tools import StopWatch
from users.decorators import login_required_ajax
from users.models import Repository_User
from .duplicates_finder import find_duplicates
from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES


@login_required
def duplicates_finder(request):
    request.breadcrumbs([("Duplicates Finder", "")])
    return render(request, "duplicates_finder.html", {
        "kill_chain_phases": {item['phase_id']: item['name'] for item in KILL_CHAIN_PHASES
                              }})


@login_required_ajax
def ajax_load_duplicates(request, typ):
    try:
        local = request.body
        duplicates = find_duplicates(typ, local)
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
        parents = StixBacklink.objects.get(id=id_).edges
        return JsonResponse(parents, status=200)
    except DoesNotExist as e:
        return JsonResponse({
            'Not found': id_ + ' has no backlinks'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
def ajax_merge_objects(request):
    raw_body = json.loads(request.body)
    original, duplicate, type = raw_body['original'], raw_body['duplicate'], raw_body['type']
    parents_of_duplicate, parents_of_original = {}, {}

    try:
        parents_of_duplicate = StixBacklink.objects.get(id=duplicate).edges
    except DoesNotExist as e:
        pass
    try:
        parents_of_original = StixBacklink.objects.get(id=original).edges
    except DoesNotExist as e:
        pass
    new_parents = parents_of_duplicate.copy()
    new_parents.update(parents_of_original)
    if new_parents:
        get_db().stix_backlinks.update({'_id': original}, {'$set': {'value': new_parents}}, upsert=True)
    if parents_of_duplicate:
        get_db().stix_backlinks.remove({'_id': duplicate})
    get_db().stix.remove({'_id': duplicate})

    map_table = {duplicate: original}

    for _id, type in parents_of_duplicate.iteritems():
        stix_remp = EdgeObject.load(_id).to_ApiObject()
        stix_remp.remap(map_table)
        ip = InboxProcessorForBuilders(user=request.user, trustgroups=None)
        ip.add(InboxItem(api_object=stix_remp, etlp='GREEN', esms=''))
        ip.run()

    return JsonResponse({
        'validation_message': 'Merged'
    }, status=200)


@csrf_exempt
def ajax_import(request, username):
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
