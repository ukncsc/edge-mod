from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
import json
from edge.inbox import InboxItem
from edge import IDManager, LOCAL_ALIAS
from users.models import Draft
from stix.utils import set_id_namespace
from edge.generic import EdgeObject
from edge.generic import create_package
from edge.inbox import InboxProcessorForPackages
from edge.tools import rgetattr

from adapters.certuk_mod.extract.ioc_wrapper import parse_file, IOCParseException
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from adapters.certuk_mod.retention.purge import STIXPurge
from adapters.certuk_mod.audit.handlers import log_activity
from users.decorators import login_required_ajax
from django.http import JsonResponse


@csrf_exempt
@login_required
def extract_upload2(request):
    file_import = request.FILES['import']
    try:
        stream = parse_file(file_import)
        #print stream
    except IOCParseException as e:
        return error_with_message(request, "Error parsing file: " + e.message)
    try:
        ip = InboxProcessorForPackages(user=request.user, streams=[(stream, None)])
    except Exception as e:
        return error_with_message(request, "Error parsing stix xml: " + e.message)

    indicators = [inbox_item for id, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'ind']
    count = 0
    ids = []
    type_names = []
    type_name_safe = []
    for indicator in indicators:
        indicator.api_object.obj.title = "StixPDFExtract" + str(count)
        count += 1
        ids.append(str(indicator.id))
        try:
            type_name = str(indicator.api_object.obj.indicator_types.pop())
        except IndexError as e:
            type_name = "Unknown"
        type_names.append(type_name)
        type_name_safe.append(type_name.replace(" ", ""))

    ip.run()
    return render(request, "extract_upload_complete.html",
                  {'indicator_information': zip(ids, type_names, type_name_safe), 'indicator_ids': json.dumps(ids)});


@login_required
def error_with_message(request, msg):
    return render(request, "not_clonable.html", {"msg": msg})


from edge.inbox import InboxProcessorForBuilders


@csrf_exempt
@login_required
def extract_upload(request):
    file_import = request.FILES['import']
    try:
        stream = parse_file(file_import)
        #print stream.buf
    except IOCParseException as e:
        return error_with_message(request, "Error parsing file: " + e.message)
    try:
        ip = DedupInboxProcessor(validate=False, user=request.user, streams=[(stream, None)])
    except Exception as e:
        return error_with_message(request, "Error parsing stix xml: " + e.message)

    ip.run()
    indicators = [inbox_item for id, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'ind']
    observables = [inbox_item for id, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'obs']
    observable_ids = {id for id, inbox_item in ip.contents.iteritems() if inbox_item.api_object.ty == 'obs'}

    if not len(indicators):
        return error_with_message(request, "No indicators found when parsing file " + str(file_import))

    # for observable in observables:
    #    loaded_obs = EdgeObject.load(observable.id)
    #    Draft.upsert('obs', loaded_obs.to_draft(), request.user)

    ids = []
    type_names = []
    type_name_safe = []
    for indicator in indicators:
        loaded_indicator = EdgeObject.load(indicator.id)

        try:
            type_name = str(loaded_indicator.obj.indicator_types.pop())
        except IndexError as e:
            type_name = "Unknown"

        loaded_indicator.obj.title = str(
            file_import) + ":" + type_name  # ToDo, remove this, ioc_parser should do this or similar. email sent to Jason

        draft_indicator = loaded_indicator.to_draft()
        inbox_processor = InboxProcessorForBuilders(user=request.user)
        empty_package = True
        for obs in draft_indicator['observables']:
            # If de-duped, the id won't be in the observable_ids
            if obs['id'] in observable_ids:
                del obs['id']
            else:
                empty_package = False
                loaded_obs = EdgeObject.load(obs['id'])
                loaded_obs.obj.sighting_count -= 1  # Sightings count was incremented. Do we want to do this? The builder won't reincrement sadly.
                inbox_processor.add(InboxItem(
                        api_object=loaded_obs.to_ApiObject(),
                        etlp=loaded_obs.etlp,
                        etou=loaded_obs.etou,
                        esms=loaded_obs.esms
                ))

        if not empty_package:
            inbox_processor.run()

        Draft.upsert('ind', draft_indicator, request.user)
        ids.append(str(indicator.id))

        type_names.append(type_name)
        type_name_safe.append(type_name.replace(" ", ""))

    ids_to_delete = [id for id, inbox_item in ip.contents.iteritems()]
    for page_index in range(0, len(ids_to_delete), 10):
        try:
            chunk_ids = ids_to_delete[page_index: page_index + 10]
            STIXPurge.remove(chunk_ids)
        except Exception as e:
            log_activity('system', 'AGEING', 'ERROR', e.message)

    return render(request, "extract_upload_complete.html",
                  {'indicator_information': zip(ids, type_names, type_name_safe), 'indicator_ids': json.dumps(ids)});


def format_draft_observable(d, indent=0):
    result = ""
    for key, value in d.iteritems():
        if isinstance(value, dict):
            result += format_draft_observable(value, indent + 1)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result += format_draft_observable(item, indent + 1)
                else:
                    result += '\t' * (indent + 1) + str(item)
        elif value and value != 'None' and key != 'id' and key != 'id_ns' and key != 'objectType':
            result += '\t' * (indent + 1) + value
    return result


def observable_to_name(observable):
    if 'id' in observable:
        return observable['id']
    return "draft: " + observable['objectType'] + ":" + format_draft_observable(observable, indent=1)

from mongoengine.connection import get_db


def get_backlinks(id):
    query = {
        '_id': {
            '$in': [id]
        },
    }

    ids = get_db().stix_backlinks.find(query, {
        'value': 1
        # stix_backlinks doesn't contain the hash unfortunately...
    })

    id_result = []
    for doc in ids:
        id_result.extend(doc['value'].keys())

    return id_result


@login_required_ajax
def extract_visualiser_get(request, id_):
    def build_title(node):
        node_type = node.summary.get("type")
        try:
            title = {
                "ObservableComposition": node.obj.observable_composition.operator
            }.get(node_type, node.id_)
        except Exception as e:
            #print e
            title = node.id_
        return title

    def iterate_draft(draft_object):
        nodes = []
        links = []
        nodes.append(dict(id=draft_object['id'], type='ind', title="draft: " + draft_object['title'], depth=0))
        count = 1
        id_to_idx = {}
        for observable in draft_object['observables']:
            id_ = observable['id'] if 'id' in observable else count
            nodes.append(dict(id=id_, type='obs', title=observable_to_name(observable), depth=1))
            links.append({"source": 0, "target": count})
            id_to_idx[id_] = count

            if 'id' in observable:
                parent_count = count
                backlink_ids = get_backlinks(observable['id'])
                for back_link_id in backlink_ids: #Should be observable compositions

                    back_link_obj = EdgeObject.load(back_link_id)
                    if back_link_id not in id_to_idx:
                        count += 1
                        nodes.append(dict(id=back_link_id, type=back_link_obj.ty, title=build_title(back_link_obj), depth=2))
                        id_to_idx[back_link_id] = count

                        second_backlink_ids = get_backlinks(back_link_id)
                        second_parent_count = id_to_idx[back_link_id]

                        for second_backlink_id in second_backlink_ids: #Probably indicators
                            second_back_link_obj = EdgeObject.load(second_backlink_id)
                            if second_backlink_id not in id_to_idx:
                                count += 1
                                nodes.append(dict(id=second_backlink_id, type=second_back_link_obj.ty, title=build_title(second_back_link_obj), depth=1))
                                id_to_idx[second_backlink_id] = count

                            links.append({"source": id_to_idx[second_backlink_id], "target": second_parent_count })
                    links.append({"source":id_to_idx[back_link_id] , "target": parent_count })

            count += 1

        return dict(nodes=nodes, links=links)

    try:
        draft_object = Draft.load(id_, request.user)
        graph = iterate_draft(draft_object)
        return JsonResponse(graph, encoder=DjangoIgnoreNonAsciiJSONEncoder, status=200)
    except Exception as e:
        return

from django.core.serializers.json import DjangoJSONEncoder

class DjangoIgnoreNonAsciiJSONEncoder(DjangoJSONEncoder):
    def __init__(self, **kwargs):
        kwargs['ensure_ascii'] = False
        kwargs['encoding'] = 'ascii'
        super(DjangoJSONEncoder, self).__init__(**kwargs)

def convert_to_viewable_obs(observable):
    new_obs = {'id': observable['id']}
    new_obs['object'] = {'properties': {'xsi:type': observable['objectType']}}
    new_obs['description'] = observable_to_name(observable)  # Technically not description!
    return new_obs

from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo

@login_required_ajax
def extract_visualiser_item_get(request, id_):
    try:
        root_edge_object = PublisherEdgeObject.load(id_)
        package = PackageGenerator.build_package(root_edge_object)
        validation_info = PackageValidationInfo.validate(package)
        return JsonResponse({
            "root_id": id_,
            "package": package.to_dict(),
            "validation_info": validation_info.validation_dict
        }, status=200)
    except Exception as e:
        pass


    try:
        draft_object = Draft.load(id_, request.user)
        package = {'indicators': [draft_object]}
        return JsonResponse({
            "root_id": id_,
            "package": package,
            "validation_info": {}
        }, status=200)
    except Exception as e:
        drafts = Draft.list(request.user, 'ind')
        for draft in drafts:
            for obs in draft['draft']['observables']:
                if 'id' in obs and obs['id'] == id_:
                    return JsonResponse({
                        "root_id": id_,
                        "package": {'observables': {'observables': [convert_to_viewable_obs(obs)]}},
                        "validation_info": {}
                    }, status=200)
        return JsonResponse(dict(e), status=500)
