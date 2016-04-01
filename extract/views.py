import json

from users.decorators import login_required_ajax
from users.models import Draft
from mongoengine.connection import get_db

from edge.inbox import InboxItem, InboxProcessorForBuilders, InboxError
from edge.generic import EdgeObject, EdgeError
from edge.tools import rgetattr
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

from adapters.certuk_mod.retention.purge import STIXPurge
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from adapters.certuk_mod.extract.ioc_wrapper import parse_file, IOCParseException
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from adapters.certuk_mod.common.views import error_with_message

@login_required
def extract(request):
    request.breadcrumbs([("Extract Stix", "")])
    return render(request, "extract_upload_form.html")

@login_required
def extract_upload(request):
    def process_observables_for_draft():
        inbox_processor = InboxProcessorForBuilders(user=request.user)
        for obs in draft_indicator['observables']:
            if obs['id'] in observable_ids:
                pass
            else:  # If de-duped, the id won't be in the observable_ids
                loaded_obs = EdgeObject.load(obs['id'])
                loaded_obs.obj.sighting_count -= 1  # Sightings count was incremented in dedup - undo
                inbox_processor.add(InboxItem(
                        api_object=loaded_obs.to_ApiObject(),
                        etlp=loaded_obs.etlp,
                        etou=loaded_obs.etou,
                        esms=loaded_obs.esms
                ))

        if inbox_processor.contents:
            inbox_processor.run()

    def remove_from_db(ids):
        for page_index in range(0, len(ids), 10):
            try:
                chunk_ids = ids[page_index: page_index + 10]
                STIXPurge.remove(chunk_ids)
            except Exception as e:
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

    type_names = []
    for indicator in indicators:
        loaded_indicator = EdgeObject.load(indicator.id)

        types = loaded_indicator.apidata['indicator_types']
        type_names.append(str(types[0]['value']) if types else "Unknown")

        draft_indicator = loaded_indicator.to_draft()
        process_observables_for_draft()
        Draft.upsert('ind', draft_indicator, request.user)

    remove_from_db(indicator_ids + list(observable_ids))

    safe_type_names = [type_name.replace(" ", "") for type_name in type_names]
    return render(request, "extract_visualiser.html",
                  {'indicator_information': zip(indicator_ids, type_names, safe_type_names),
                   'indicator_ids': json.dumps(indicator_ids)});


def summarise_draft_observable(d, indent=0):
    result = ""
    for key, value in d.iteritems():
        if isinstance(value, dict):
            result += summarise_draft_observable(value, indent + 1)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result += summarise_draft_observable(item, indent + 1)
                else:
                    result += '\t' * (indent + 1) + str(item)
        elif value and value != 'None' and key != 'id' and key != 'id_ns' and key != 'objectType':
            result += '\t' * (indent + 1) + value
    return result


def observable_to_name(observable, is_draft):
    if is_draft:
        return "draft: " + observable['objectType'] + ":" + summarise_draft_observable(observable, indent=1)
    return observable['id']


def get_backlinks(id_, eo_filter):
    ids = get_db().stix_backlinks.find({
        '_id': {
            '$in': [id_]
        },
    }, {
        'value': 1
    })

    bl_ids = []
    for doc in ids:
        bl_ids.extend(doc['value'].keys())

    def eo_filter_generator():
        for eoId in bl_ids:
            try:
                eo = EdgeObject.load(eoId)
            except EdgeError as _:
                continue
            if eo_filter(eo):
                yield eo

    return [x for x in eo_filter_generator()]


@login_required_ajax
def extract_visualiser_get(request, id_):
    def is_observable_composition(eo):
        try:
            eo.obj.observable_composition
        except AttributeError as _:
            return False
        return True

    def is_indicator(eo):
        return "ind" in eo.ty

    def build_title(node):
        node_type = node.summary.get("type")
        try:
            title = {
                "ObservableComposition": node.obj.observable_composition.operator
            }.get(node_type, node.id_)
        except AttributeError as e:
            title = node.id_
        return title

    def iterate_draft():

        class Counter:
            idx = 0

        def append_node(data):
            nodes.append(data)
            Counter.idx += 1

        def is_draft(type_, obs_id):
            return obs_id in {x['draft']['id'] for x in Draft.list(request.user, type_) if 'id' in x['draft']}

        def is_deduped(obs_id):
            return not is_draft('obs', obs_id)

        nodes = []
        links = []

        append_node(dict(id=draft_object['id'], type='ind', title="draft: " + draft_object['title'], depth=0))

        id_to_idx = {}
        for observable in draft_object['observables']:
            obs_id = observable['id'] if is_deduped(observable['id']) else Counter.idx
            id_to_idx[obs_id] = Counter.idx
            append_node(dict(id=obs_id, type='obs', title=observable_to_name(observable, is_draft('obs', obs_id)), depth=1))

            links.append({"source": 0, "target": id_to_idx[obs_id]})

            if is_deduped(obs_id):
                for obs_composition in get_backlinks(observable['id'], is_observable_composition):
                    if obs_composition.id_ not in id_to_idx:
                        for indicator_obj in get_backlinks(obs_composition.id_, is_indicator):
                            if indicator_obj.id_ not in id_to_idx:
                                id_to_idx[indicator_obj.id_] = Counter.idx
                                append_node(dict(id=indicator_obj.id_, type=indicator_obj.ty,
                                                 title=build_title(indicator_obj), depth=2))

                            links.append({"source": id_to_idx[indicator_obj.id_], "target": id_to_idx[obs_id]})

        return dict(nodes=nodes, links=links)

    try:
        draft_object = Draft.load(id_, request.user)
        graph = iterate_draft()
        return JsonResponse(graph, status=200)
    except EdgeError as e:
        return JsonResponse(dict(e), status=500)


@login_required_ajax
def extract_visualiser_item_get(request, id_):
    def build_ind_package_from_draft(ind):
        return {'indicators': [ind]}

    def get_draft_obs():
        # For extracts, draft obs are contained within their indicator, not within the Draft obs list
        for draft_ind in Draft.list(request.user, 'ind'):
            obs_dict = {obs['id']: obs for obs in draft_ind['draft']['observables'] if 'id' in obs}
            if id_ in obs_dict:
                return obs_dict.get(id_)

        return None

    def convert_draft_to_viewable_obs(observable):
        view_obs = dict(id=observable['id'])
        view_obs['object'] = {'properties':
                                  {'xsi:type': observable['objectType'],
                                   'value': observable_to_name(observable, get_draft_obs())}}
        return view_obs

    def is_draft_ind():
        return id_ in {x['draft']['id'] for x in Draft.list(request.user, 'ind') if 'id' in x['draft']}

    def build_obs_package_from_draft(obs):
        return {'observables': {'observables': [convert_draft_to_viewable_obs(obs)]}}

    try:  # Non-draft
        root_edge_object = PublisherEdgeObject.load(id_)
        package = PackageGenerator.build_package(root_edge_object)
        validation_info = PackageValidationInfo.validate(package)
        return JsonResponse({
            "root_id": id_,
            "package": package.to_dict(),
            "validation_info": validation_info.validation_dict
        }, status=200)
    except EdgeError as e:
        pass

    try:  # Draft
        if is_draft_ind():
            package = build_ind_package_from_draft(Draft.load(id_, request.user))
        else:
            draft_obs = get_draft_obs()
            if draft_obs:
                package = build_obs_package_from_draft(draft_obs)
            else:
                return JsonResponse({'value': 'not found'}, status=500)

        return JsonResponse({
            "root_id": id_,
            "package": package,
            "validation_info": {}
        }, status=200)
    except Exception as e:
        return JsonResponse(dict(e), status=500)
