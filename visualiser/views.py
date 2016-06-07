import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from edge.generic import EdgeError

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.common.objectid import discover as objectid_discover
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from adapters.certuk_mod.visualiser.graph import create_graph

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

@login_required_ajax
def visualiser_get(request, id_):
    try:
        root_edge_object = PublisherEdgeObject.load(id_)
        graph = create_graph([(0, None, root_edge_object, "edge")], [], [], [], [])
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
    except EdgeError as e:
        if e.message == id_ + " not found":
            return JsonResponse({'error': e.message}, status=404)
        else:
            return JsonResponse({'error': e.message}, status=500)
    except Exception as e:
        return JsonResponse(dict(e), status=500)


@login_required_ajax
def visualiser_get_extended(request):
    json_data = json.loads(request.body)
    root_id = json_data['id']
    bl_ids = json_data['id_bls']
    id_matches = json_data['id_matches']
    hide_edge_ids = json_data['hide_edge_ids']
    show_edge_ids = json_data['show_edge_ids']
    try:
        root_edge_object = PublisherEdgeObject.load(root_id)
        graph = create_graph([(0, None, root_edge_object, "edge")], bl_ids, id_matches, hide_edge_ids, show_edge_ids)
        return JsonResponse(graph, status=200)
    except Exception as e:
        return JsonResponse(dict(e), status=500)
