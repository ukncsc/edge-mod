from edge.generic import EdgeObject, EdgeError
from mongoengine.connection import get_db
from adapters.certuk_mod.common.objectid import get_type_string


REL_TYPE_EDGE = "edge"
REL_TYPE_MATCH = "match"
REL_TYPE_BACKLINK = "backlink"
REL_TYPE_DRAFT = "draft"
REL_TYPE_EXT = "external_ref"

NODE_TYPE_DRAFT = "draft"
NODE_TYPE_EXT = "external_ref"
NODE_TYPE_NORM = "normal"

LINK_TO_NODE_TYPE = {
    REL_TYPE_EDGE: NODE_TYPE_NORM,
    REL_TYPE_MATCH: NODE_TYPE_NORM,
    REL_TYPE_BACKLINK: NODE_TYPE_NORM,
    REL_TYPE_DRAFT: NODE_TYPE_DRAFT,
    REL_TYPE_EXT: NODE_TYPE_EXT
}


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


def get_matches(id_, request):
    eo = EdgeObject.load(id_, request.user.filters())
    return [doc['_id'] for doc in
            get_db().stix.find({'data.hash': eo.doc['data']['hash'], 'type': eo.ty, '_id': {'$ne': eo.id_}},
                               {'_id': 1})]


def backlinks_exist(id_):
    return get_backlinks(id_).count()


def matches_exist(id_, request):
    return len(get_matches(id_, request))


ID_TYPE_ALIAS = {
        "campaign": "cam",
        "courseofaction": "coa",
        "et": "tgt",
        "threatactor": "act",
        "incident": "inc",
        "indicator": "ind",
        "observable": "obs",
        "package": "pkg",
        "stix": "pkg"
}

def create_graph(stack, bl_ids, id_matches, hide_edge_ids, show_edge_ids, hidden_ids, request):
    def show_edges(rel_type, node_id):
        return ((REL_TYPE_BACKLINK != rel_type and REL_TYPE_MATCH != rel_type) or (node_id in show_edge_ids)) and \
               (node_id not in hide_edge_ids)

    nodes = []
    links = []

    def create_external_reference(edge):
        summary = {'title': edge.id_, 'type': edge.ty, 'value': '', '_id': edge.id_, 'cv': '', 'tg': '',
                   'data': {'idns': '', 'etlp': '', 'summary': {'title': edge.id_},
                            'hash': '', 'api': ''}, 'created_by_organization': ''}
        return EdgeObject(summary)

    def create_external_reference_from_id(id):
        type_string = get_type_string(id)
        type_string = ID_TYPE_ALIAS.get(type_string.lower(), type_string)

        summary = {'title': id, 'type': type_string, 'value': '', '_id': id, 'cv': '', 'tg': '',
                   'data': {'idns': '', 'etlp': '', 'summary': {'title': id},
                            'hash': '', 'api': ''}, 'created_by_organization': ''}
        return EdgeObject(summary)

    def get_node_type(rel_type):
        return LINK_TO_NODE_TYPE[rel_type]
    id_to_idx = {}

    while stack:
        depth, parent_idx, node, rel_type = stack.pop()
        node_id = node.id_
        if node_id in hidden_ids:
            continue
        node_type = get_node_type(rel_type)
        is_new_node = node_id not in id_to_idx
        if is_new_node:
            idx = len(nodes)
            id_to_idx[node_id] = idx
            title = node.summary.get("title", None)
            if title is None:
                title = build_title(node)
            if node_type is NODE_TYPE_EXT or node_type is NODE_TYPE_DRAFT:
                backlinks, matches = False, False
            else:
                backlinks, matches, = backlinks_exist(node_id), matches_exist(node_id, request)

            nodes.append(dict(id=node_id, type=node.ty, title=title, depth=depth, node_type=node_type,
                              has_backlinks=backlinks, has_matches=matches, has_edges=len(node.edges) != 0,
                              edges_shown=show_edges(rel_type, node_id), matches_shown=node_id in id_matches,
                              backlinks_shown=node_id in bl_ids))
        else:
            idx = id_to_idx[node_id]

        if parent_idx is not None:
            links.append({"source": parent_idx, "target": idx, "rel_type": rel_type})

        if is_new_node:
            if show_edges(rel_type, node_id):
                for edge in node.edges:
                    try:
                        stack.append((depth + 1, idx, edge.fetch(), REL_TYPE_EDGE))
                    except EdgeError as e:
                        if e.message == edge.id_ + " not found":
                            obj = create_external_reference(edge)
                            stack.append((depth + 1, idx, obj, REL_TYPE_EXT))
                            continue
                    except Exception as e:
                        raise e
            if node_id in bl_ids:
                for eoId in [val for doc in get_backlinks(node_id) for val in doc['value'].keys()]:
                    try:
                        stack.append((depth + 1, idx, EdgeObject.load(eoId, request.user.filters()), REL_TYPE_BACKLINK))
                    except:
                        obj = create_external_reference_from_id(eoId)
                        stack.append((depth + 1, idx, obj, REL_TYPE_EXT))

            if node_id in id_matches:
                for eoId in get_matches(node_id, request):
                    try:
                        stack.append((depth + 1, idx, EdgeObject.load(eoId, request.user.filters()), REL_TYPE_MATCH))
                    except:
                        obj = create_external_reference_from_id(eoId)
                        stack.append((depth + 1, idx, obj, REL_TYPE_EXT))

    return dict(nodes=nodes, links=links)
