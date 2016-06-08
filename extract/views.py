import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse

from users.decorators import login_required_ajax
from edge.inbox import InboxError

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.retention.purge import STIXPurge
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from adapters.certuk_mod.extract.ioc_wrapper import parse_file, IOCParseException
from adapters.certuk_mod.common.views import error_with_message
from adapters.certuk_mod.common.objectid import is_valid_stix_id
from adapters.certuk_mod.visualiser.views import visualiser_item_get
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.extract.extract_actions import *

DRAFT_ID_SEPARATOR = ":draft:"


@login_required
def extract(request):
    request.breadcrumbs([("Extract Stix", "")])
    return render(request, "extract_upload_form.html")


@login_required_ajax
def extract_upload(request):
    def process_draft_obs():
        for obs in draft_indicator['observables']:
            if obs['id'] in observable_ids:  # Is it a draft?
                del obs['id']
                if not obs['title']:
                    obs['title'] = summarise_draft_observable(obs)

    def remove_from_db(ids):
        for page_index in range(0, len(ids), 10):
            try:
                chunk_ids = ids[page_index: page_index + 10]
                STIXPurge.remove(chunk_ids)
            except Exception:
                pass

    file_import = request.FILES['import']
    try:
        stream = parse_file(file_import)
    except IOCParseException as e:
        return error_with_message(request,
                                  "Error parsing file: " + e.message + " content from parser was " + stream.buf)
    try:
        ip = DedupInboxProcessor(validate=False, user=request.user, streams=[(stream, None)])
    except InboxError as e:
        return error_with_message(request,
                                  "Error parsing stix xml: " + e.message + " content from parser was " + stream.buf)
    ip.run()

    indicators = [inbox_item for _, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'ind']
    if not len(indicators):
        return error_with_message(request, "No indicators found when parsing file " + str(file_import))

    indicator_ids = [id_ for id_, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'ind']
    observable_ids = {id_ for id_, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'obs'}

    try:
        for indicator in indicators:
            draft_indicator = EdgeObject.load(indicator.id).to_draft()
            process_draft_obs()
            Draft.upsert('ind', draft_indicator, request.user)
    finally:
        remove_from_db(indicator_ids + list(observable_ids))

    return redirect("extract_visualiser",
                    ids=json.dumps(indicator_ids))


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

        return JsonResponse(iterate_draft(Draft.load(id_, request.user), [], [], [], []), status=200)
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
        return node_id in {x['draft']['id'] for x in Draft.list(request.user, 'ind') if 'id' in x['draft']}

    def build_obs_package_from_draft(obs):
        return {'observables': {'observables': [convert_draft_to_viewable_obs(obs)]}}

    try:
        validation_dict = {}
        if DRAFT_ID_SEPARATOR in node_id:  # draft obs
            package_dict = build_obs_package_from_draft(get_draft_obs(node_id, request.user))
        elif is_draft_ind():
            package_dict = build_ind_package_from_draft(Draft.load(node_id, request.user))
        else:  # Non-draft
            return visualiser_item_get(request, node_id)

        return JsonResponse({
            "root_id": node_id,
            "package": package_dict,
            "validation_info": validation_dict
        }, status=200)
    except Exception as e:
        return JsonResponse({"error": e.message}, status=500)


@login_required_ajax
def extract_visualiser_merge_observables(request):
    merge_data = json.loads(request.body)
    if not is_valid_stix_id(merge_data['id']):
        return JsonResponse({'message': "Invalid stix id: " + merge_data['id']}, status=200)

    draft_ind = Draft.load(merge_data['id'], request.user)
    draft_obs_offsets = [get_draft_obs_offset(draft_ind, id_) for id_ in merge_data['ids'] if DRAFT_ID_SEPARATOR in id_]

    hash_types = ['MD5', 'MD6', 'SHA1', 'SHA224', 'SHA256', 'SHA384', 'SHA512', 'SSDeep', 'Other']
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
    draft_ind = Draft.load(delete_data['id'], request.user)
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
    try:
        return JsonResponse(
            iterate_draft(Draft.load(root_id, request.user), bl_ids, id_matches, hide_edge_ids, show_edge_ids),
            status=200)
    except Exception as e:
        pass

    try:
        root_edge_object = PublisherEdgeObject.load(root_id)
        graph = create_graph([(0, None, root_edge_object, "edge")], [], [], [], [])
        return JsonResponse(graph, status=200)
    except Exception as e:
        return JsonResponse({'error': e.message}, status=400)
