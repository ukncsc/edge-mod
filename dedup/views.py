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
from edge.inbox import InboxError, InboxProcessor, InboxItem
from edge.generic import EdgeObject
from edge.models import StixBacklink
from edge.tools import StopWatch
from users.decorators import login_required_ajax
from users.models import Repository_User
from .duplicates_finder import find_duplicates
from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES


def remap_parent_objects(parents, duplicate, map_table, user):
    ip = InboxProcessor(user=user, trustgroups=None)
    validation_message = {}
    for _id in parents.keys():
        try:
            api_obj = EdgeObject.load(_id).to_ApiObject()
            api_obj.remap(map_table)
            ip.add(InboxItem(api_object=api_obj, etlp='NULL', esms=''))
        except InboxError as e:
            return JsonResponse({
                'message': e.message
            }, status=500)
    try:
        ip.run()
    except InboxError as e:
        return JsonResponse({
            'message': e.message
        }, status=500)
    get_db().stix.remove({'_id': {
        '$in': duplicate}})
    return validation_message


def remap_backlinks(original, duplicate, type):
    parents_of_original, parents_of_duplicate = calculate_backlinks(original, duplicate)

    # new_parents = parents_of_duplicate.copy()
    # new_parents.update(parents_of_original)
    # if new_parents:
    #     get_db().stix_backlinks.update({'_id': original}, {'$set': {'value': new_parents}}, upsert=True)
    if parents_of_duplicate:
        get_db().stix_backlinks.remove({'_id': {'$in': duplicate}})

    return parents_of_original, parents_of_duplicate


def calculate_backlinks(original, duplicate):
    parents_of_original, parents_of_duplicate = {}, {}
    try:
        parents_of_original = StixBacklink.objects.get(id=original).edges
    except DoesNotExist as e:
        pass
    for dup in duplicate:
        try:
            parents_of_duplicate.update(StixBacklink.objects.get(id=dup).edges)
        except DoesNotExist as e:
            pass
    return parents_of_original, parents_of_duplicate


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
def ajax_load_parent_ids(request):
    result = {}
    try:
        raw_body = json.loads(request.body)
        original, duplicate = raw_body.get('original'), raw_body.get('duplicate')
        parents_of_original, parents_of_duplicate = calculate_backlinks(original, duplicate)
        for _id in parents_of_original.keys():
            result.setdefault('original', []).append(_id)
        for _id in parents_of_duplicate.keys():
            result.setdefault('duplicate', []).append(_id)
        return JsonResponse(result, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


@login_required_ajax
def ajax_merge_objects(request):
    try:
        user = request.user
        raw_body = json.loads(request.body)
        original, duplicate, _type = raw_body.get('original'), raw_body.get('duplicate'), raw_body['type']
        parents_of_original, parents_of_duplicate = remap_backlinks(original, duplicate, type)

        map_table = {dup: original for dup in duplicate}
        validation_message = remap_parent_objects(parents_of_duplicate, duplicate, map_table, user)

        # log_activity(user, 'DEDUP', 'INFO', validation_message)
        return JsonResponse({
            'validation_message': 'Merged'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'message': e.message
        }, status=500)


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
