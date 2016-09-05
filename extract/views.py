import json

from mongoengine import DoesNotExist
from defusedxml import EntitiesForbidden
from lxml.etree import XMLSyntaxError

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from users.decorators import login_required_ajax
from edge.inbox import InboxError
from edge.tools import StopWatch

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.retention.purge import STIXPurge
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from adapters.certuk_mod.extract.ioc_wrapper import parse_file, IOCParseException

from adapters.certuk_mod.common.objectid import is_valid_stix_id
from adapters.certuk_mod.visualiser.views import visualiser_item_get
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.extract.extract_actions import *
from adapters.certuk_mod.common.activity import save as log_activity

import datetime
import threading
import uuid

import adapters.certuk_mod.extract.extract_store as extract_store

DRAFT_ID_SEPARATOR = ":draft:"


@login_required
def extract(request):
    request.breadcrumbs([("Extract Stix", "")])
    return render(request, "extract_upload_form.html")


@login_required
def uploaded_stix_extracts(request):
    request.breadcrumbs([("Extract Stix", "")])
    return render(request, "extract_status.html")


@login_required_ajax
def extract_upload(request):
    file_import = request.FILES.get('import', "");
    extract_id = extract_store.create(request.user.username, str(file_import))

    if 'import' not in request.FILES:
        extract_store.update(extract_id, "FAILED", "Error in file upload", [])
        return JsonResponse({'result': str(extract_id)}, status=200)

    try:
        stream = parse_file(file_import)
    except IOCParseException as e:
        extract_store.update(extract_id,
                             "FAILED",
                             "Error parsing file: %s content from parser was %s" % (e.message, stream.buf),
                             [])

        return JsonResponse({'result': str(extract_id)}, status=200)

    threading.Thread(target=process_stix,
                     args=(stream, request.user, extract_id, str(file_import))).start()

    return JsonResponse({'result': str(extract_id)}, status=200)


def create_extract_json(extract):
    dt_in = extract['timestamp']
    offset = datetime.datetime.now(settings.LOCAL_TZ).isoformat()[-6:]
    time_string = dt_in.isoformat() + offset
    visualiser_url = "/adapter/certuk_mod/extract_visualiser/" + json.dumps(extract['draft_ids']) \
        if (extract['state'] == "COMPLETE") else ""
    return {'message': extract['message'],
            'filename': extract['filename'],
            'state': extract['state'],
            'datetime': time_string,
            'visualiser_url': visualiser_url,
            'id': str(extract['_id'])}


@login_required_ajax
def extract_status(request):
    id = request.body
    if id.startswith('"') and id.endswith('"'):
        id = id[1:-1]
    extract = extract_store.get(id)
    if extract:
        return JsonResponse({'result': create_extract_json(extract)}, status=200)

    return JsonResponse({'result': "Unknown Error. Unable to find extract"}, status=500)


@login_required_ajax
def delete_extract(request):
    id = request.body
    if id.startswith('"') and id.endswith('"'):
        id = id[1:-1]
    extract = extract_store.get(id)
    if extract:
        for draft_indicator_id in extract['draft_ids']:
            Draft.maybe_delete(draft_indicator_id, request.user)

        extract_store.delete(id)
    return HttpResponse(status=204)


@login_required_ajax
def extract_list(request):
    extracts = extract_store.find(user=request.user.username)
    extracts_json = [create_extract_json(extract) for extract in extracts]

    return JsonResponse({'result': extracts_json}, status=200)


def process_stix(stream, user, extract_id, file_name):
    elapsed = StopWatch()

    def log_extract_activity_message(message):
        duration = int(elapsed.ms())
        return "@ %dms : %s\n" % (duration, message)

    def process_draft_obs():
        # draft_indicator['observables'] contains all obs for the ind. observable_ids just the inboxed
        # (i.e. not de-duped)
        # If it is not de-duped, dump the id as this confuses the builder; and gives us a quick way to differentiate.
        for obs in draft_indicator['observables']:
            if obs['id'] in observable_ids:  # Is it a draft?
                del obs['id']
                if not obs['title']:
                    obs['title'] = summarise_draft_observable(obs)

    def remove_from_db(ids):
        PAGE_SIZE = 100
        for page_index in range(0, len(ids), PAGE_SIZE):
            try:
                chunk_ids = ids[page_index: page_index + PAGE_SIZE]
                STIXPurge.remove(chunk_ids)
            except Exception:
                pass

    log_message = log_extract_activity_message("DedupInboxProcessor parse")

    extract_store.update(extract_id, "PROCESSING", "", [])

    try:
        ip = DedupInboxProcessor(validate=False, user=user, streams=[(stream, None)])
    except (InboxError, EntitiesForbidden, XMLSyntaxError) as e:
        extract_store.update(extract_id, "FAILED",
                             "Error parsing stix file: %s content from parser was %s" % (e.message, stream.buf), [])
        return

    log_message += log_extract_activity_message("DedupInboxProcessor run & dedup")
    ip.run()

    indicators = [inbox_item for _, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'ind']
    if not len(indicators):
        extract_store.update(extract_id, "FAILED", "No indicators found when parsing file %s" % file_name, [])
        return

    indicator_ids = [id_ for id_, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'ind']
    observable_ids = {id_ for id_, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'obs'}

    log_message += log_extract_activity_message("Create drafts from inboxed objects")
    try:
        for indicator in indicators:
            draft_indicator = EdgeObject.load(indicator.id).to_draft()
            process_draft_obs()
            Draft.upsert('ind', draft_indicator, user)
    finally:
        # The observables were fully inboxed, but we want them only to exist as drafts, so remove from db
        log_message += log_extract_activity_message("Delete inboxed objects")
        remove_from_db(indicator_ids + list(observable_ids))

    extract_store.update(extract_id, "COMPLETE", "Found %d indicators" % (len(indicator_ids)), indicator_ids)

    log_message += log_extract_activity_message("Redirect user to visualiser")
    log_activity(user.username, 'EXTRACT', 'INFO', log_message)


@login_required
def extract_visualiser(request, ids):
    request.breadcrumbs([("Extract Visualiser", "")])

    indicator_ids = [id_ for id_ in json.loads(ids) if is_valid_stix_id(id_)]

    type_names = []
    indicator_ids_to_remove = []
    for ind_id in indicator_ids:
        try:
            type_names.append(str(Draft.load(ind_id, request.user)['indicatorType']))
        except:
            indicator_ids_to_remove.append(ind_id)

    for ind_id in indicator_ids_to_remove:
        indicator_ids.remove(ind_id)

    safe_type_names = [type_name.replace(" ", "") for type_name in type_names]
    str_ids = [str(id_) for id_ in indicator_ids]

    ind_information = []
    for item in range(0, len(str_ids)):
        ind_information.append({
            'str_id': str_ids[item],
            'type_name': type_names[item],
            'safe_type_name': safe_type_names[item]
        })

    return render(request, "extract_visualiser.html", {
        "indicator_ids": str_ids,
        "indicator_information": ind_information,
        "kill_chain_phases": {item["phase_id"]: item["name"] for item in KILL_CHAIN_PHASES}
    })


@login_required_ajax
def extract_visualiser_get(request, id_):
    try:
        if not is_valid_stix_id(id_):
            return JsonResponse({"invalid stix id: " + id_}, status=200)

        return JsonResponse(iterate_draft(Draft.load(id_, request.user), [], [], [], [], []), status=200)
    except Exception as e:
        return JsonResponse({'error': e.message}, status=400)


@login_required_ajax
def extract_visualiser_item_get(request, node_id):
    def build_ind_package_from_draft(ind):
        return {'indicators': [ind]}

    def convert_draft_to_viewable_obs(observable):
        view_obs = dict(id=node_id)
        view_obs['object'] = {'properties':
                                  {'xsi:type': observable['objectType'],
                                   'value': observable_to_name(observable, DRAFT_ID_SEPARATOR in node_id),
                                   'description': observable.get('description', '')}}

        return view_obs

    def is_draft_ind():
        try:
            Draft.load(node_id, request.user)
            return True
        except:
            return False

    def build_obs_package_from_draft(obs):
        return {'observables': {'observables': [convert_draft_to_viewable_obs(obs)]}}

    try:
        validation_dict = {}
        if DRAFT_ID_SEPARATOR in node_id:  # draft obs
            package_dict = build_obs_package_from_draft(get_draft_obs(node_id, request.user))
            type_info = [{"id_": node_id, "ty":"obs"}]
        elif is_draft_ind():
            package_dict = build_ind_package_from_draft(Draft.load(node_id, request.user))
            type_info = [{"id_": node_id, "ty":"ind"}]
        else:  # Non-draft
            return visualiser_item_get(request, node_id)

        return JsonResponse({
            "root_id": node_id,
            "package": package_dict,
            "validation_info": validation_dict,
            "type_info": type_info
        }, status=200)
    except Exception as e:
        return JsonResponse({"error": e.message}, status=500)


@login_required_ajax
def extract_visualiser_merge_observables(request):
    merge_data = json.loads(request.body)
    if not is_valid_stix_id(merge_data['id']):
        return JsonResponse({'message': "Invalid stix id: " + merge_data['id']}, status=200)

    try:
        draft_ind = Draft.load(merge_data['id'], request.user)
    except DoesNotExist:
        return JsonResponse({'Error': "Draft object:%s does not exist" % merge_data['id']}, status=400)

    draft_obs_offsets = [get_draft_obs_offset(draft_ind, id_) for id_ in merge_data['ids'] if DRAFT_ID_SEPARATOR in id_]

    hash_types = ['MD5', 'MD6', 'SHA1', 'SHA224', 'SHA256', 'SHA384', 'SHA512', 'SSDEEP', 'Other']
    (can_merge, message) = can_merge_observables(draft_obs_offsets, draft_ind, hash_types)
    if not can_merge:
        return JsonResponse({'Error': message}, status=400)

    merge_draft_file_observables(draft_obs_offsets, draft_ind, hash_types)
    Draft.maybe_delete(draft_ind['id'], request.user)
    Draft.upsert('ind', draft_ind, request.user)
    return JsonResponse({'result': "success"}, status=200)


@login_required_ajax
def extract_visualiser_delete_observables(request):
    delete_data = json.loads(request.body)
    try:
        draft_ind = Draft.load(delete_data['id'], request.user)
    except DoesNotExist:
        return JsonResponse({'Error': "Draft object:%s does not exist" % delete_data['id']}, status=400)

    draft_obs_offsets = [get_draft_obs_offset(draft_ind, id_) for id_ in delete_data['ids'] if
                         DRAFT_ID_SEPARATOR in id_]

    delete_file_observables(draft_obs_offsets, draft_ind)

    def ref_obs_generator():
        obs_id_map = {draft_ind['observables'][i]['id']: i for i in xrange(len(draft_ind['observables'])) if
                      'id' in draft_ind['observables'][i]}
        ref_obs_ids = [obs_id for obs_id in delete_data['ids'] if DRAFT_ID_SEPARATOR not in obs_id]
        for obs_id in ref_obs_ids:
            offset = obs_id_map.get(obs_id, None)
            if offset is not None:
                yield offset

    delete_file_observables([id_ for id_ in ref_obs_generator()], draft_ind)
    Draft.maybe_delete(draft_ind['id'], request.user)
    Draft.upsert('ind', draft_ind, request.user)
    return JsonResponse({'result': "success"}, status=200)


@login_required_ajax
def extract_visualiser_get_extended(request):
    json_data = json.loads(request.body)
    root_id = json_data['id']
    bl_ids = json_data['id_bls']
    id_matches = json_data['id_matches']
    hide_edge_ids = json_data['hide_edge_ids']
    show_edge_ids = json_data['show_edge_ids']
    hidden_ids = json_data['hidden_ids']
    try:
        return JsonResponse(
            iterate_draft(Draft.load(root_id, request.user), bl_ids, id_matches, hide_edge_ids, show_edge_ids,
                          hidden_ids),
            status=200)
    except Exception:
        pass

    try:
        root_edge_object = PublisherEdgeObject.load(root_id)
        graph = create_graph([(0, None, root_edge_object, REL_TYPE_EDGE)], bl_ids, id_matches, hide_edge_ids,
                             show_edge_ids, hidden_ids)
        return JsonResponse(graph, status=200)
    except Exception as e:
        return JsonResponse({'error': e.message}, status=400)
