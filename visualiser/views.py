import re
import urllib2

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from users.decorators import login_required_ajax

from edge.generic import EdgeObject


objectid_matcher = re.compile(
    # {STIX/ID Alias}:{type}-{GUID}
    r".*/([a-z][\w\d-]+:[a-z]+-[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})/?$",
    re.IGNORECASE  # | re.DEBUG
)


@login_required
def visualiser_discover(request):
    referrer = urllib2.unquote(request.META.get("HTTP_REFERER", ""))
    match = objectid_matcher.match(referrer)
    if match is not None and len(match.groups()) == 1:
        id_ = match.group(1)
        return redirect("visualiser_view", id_=id_)
    else:
        return redirect("visualiser_not_found")


@login_required
def visualiser_view(request, id_):
    return render(request, 'visualiser.html', {
        "id": id_
    })


@login_required
def visualiser_not_found(request):
    return render(request, "visualiser_not_found.html", {})


@login_required_ajax
def visualiser_get(request, id_):
    def build_title(node):
        node_type = node.summary.get("type")
        try:
            title = {
                "ObservableComposition": node.obj.observable_composition.operator
            }.get(node_type, node.id_)
        except Exception as e:
            print e
            title = node.id_
        return title

    def depth_first_iterate(root_node):
        nodes = []
        links = []
        id_to_idx = {}
        stack = [(0, None, root_node)]
        while stack:
            depth, parent_idx, node = stack.pop()
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
                links.append({"source": parent_idx, "target": idx})
            if is_new_node:
                stack.extend((depth + 1, idx, edge.fetch()) for edge in node.edges)

        return dict(nodes=nodes, links=links)

    success = False
    error_message = None
    graph = None

    try:
        root_edge_object = EdgeObject.load(id_)
        graph = depth_first_iterate(root_edge_object)
    except Exception as e:
        error_message = e.message
    else:
        success = True

    return JsonResponse({
        "success": success,
        "error_message": error_message,
        "graph": graph
    }, status=200)
