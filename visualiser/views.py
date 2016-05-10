import json
from mongoengine.connection import get_db
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from edge.generic import EdgeObject, EdgeError

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.common.objectid import discover as objectid_discover
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from users.decorators import login_required_ajax


@login_required
def visualiser_discover(request):
    return objectid_discover(request, "visualiser_view", "visualiser_not_found")


@login_required
def visualiser_view(request, id_):
    request.breadcrumbs([("Visualiser", "")])
    return render(request, 'visualiser.html', {
        "id": id_,
        "kill_chain_phases": {item['phase_id']: item['name'] for item in KILL_CHAIN_PHASES}
    })


@login_required
def visualiser_not_found(request):
    return render(request, "visualiser_not_found.html", {})


def build_title(node):
    node_type = node.summary.get("type")
    try:
        title = {
            "ObservableComposition": node.obj.observable_composition.operator
        }.get(node_type, node.id_)
    except Exception as e:
        title = node.id_
    return title


def get_backlinks(id_):
    ids = get_db().stix_backlinks.find({
        '_id': {
            '$in': [id_]
        },
    }, {
        'value': 1
    })

    return ids


def get_matches(id_):
    eo = EdgeObject.load(id_);
    return [doc['_id'] for doc in
            get_db().stix.find({'data.hash': eo.doc['data']['hash'], 'type': eo.ty, '_id': {'$ne': eo.id_}},
                               {'_id': 1})]


def depth_first_iterate(root_node, bl_ids, id_matches):
    nodes = []
    links = []
    id_to_idx = {}
    stack = [(0, None, root_node, "edge")]
    while stack:
        depth, parent_idx, node, rel_type = stack.pop()
        node_id = node.id_
        is_new_node = node_id not in id_to_idx
        if is_new_node:
            idx = len(nodes)
            id_to_idx[node_id] = idx
            title = node.summary.get("title", None)
            if title is None:
                title = build_title(node)
            nodes.append(dict(id=node_id, type=node.ty, title=title, depth=depth))
        else:
            idx = id_to_idx[node_id]
        if parent_idx is not None:
            links.append({"source": parent_idx, "target": idx, "rel_type": rel_type})
        if is_new_node:
            if "backlink" not in rel_type and "match" not in rel_type:
                stack.extend((depth + 1, idx, edge.fetch(), "edge") for edge in node.edges)
            if node_id in bl_ids:
                for eoId in [val for doc in get_backlinks(node_id) for val in doc['value'].keys()]:
                    stack.append((depth + 1, idx, EdgeObject.load(eoId), "backlink"))
            if node_id in id_matches:
                for eoId in get_matches(node_id):
                    stack.append((depth + 1, idx, EdgeObject.load(eoId), "match"))

    return dict(nodes=nodes, links=links)


@login_required_ajax
def visualiser_get(request, id_):
    try:
        root_edge_object = PublisherEdgeObject.load(id_)
        graph = depth_first_iterate(root_edge_object, [], [])
        return JsonResponse(graph, status=200)
    except Exception as e:
        return JsonResponse(dict(e), status=500)


@login_required_ajax
def visualiser_item_get(request, id_):
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
        return JsonResponse(dict(e), status=500)


@login_required_ajax
def visualiser_get_with_others(request):
    json_data = json.loads(request.body)
    root_id = json_data['id']
    bl_ids = json_data['id_bls']
    id_matches = json_data['id_matches']
    try:
        root_edge_object = PublisherEdgeObject.load(root_id)
        graph = depth_first_iterate(root_edge_object, bl_ids, id_matches)
        return JsonResponse(graph, status=200)
    except Exception as e:
        return JsonResponse(dict(e), status=500)
