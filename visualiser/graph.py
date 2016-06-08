from edge.generic import EdgeObject, EdgeError
from mongoengine.connection import get_db

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
    eo = EdgeObject.load(id_)
    return [doc['_id'] for doc in
            get_db().stix.find({'data.hash': eo.doc['data']['hash'], 'type': eo.ty, '_id': {'$ne': eo.id_}},
                               {'_id': 1})]


def backlinks_exist(id_):
    backlinks, exists = get_backlinks(id_), ''
    if backlinks.count():
        exists = True
    else:
        exists = False
    return exists


def matches_exist(id_):
    matches, exists = get_matches(id_), ''
    if len(matches):
        exists = True
    else:
        exists = False
    return exists


def create_graph(stack, bl_ids, id_matches, hide_edge_ids, show_edge_ids):
    def show_edges(rel_type, node_id):
        return ("backlink" not in rel_type and "match" not in rel_type) or (node_id in show_edge_ids)

    nodes = []
    links = []

    def create_external_reference(edge):
        summary = {'title': edge.id_, 'type': edge.ty, 'value': '', '_id': edge.id_, 'cv': '', 'tg': '',
                   'data': {'idns': '', 'etlp': '', 'summary': {'title': edge.id_},
                            'hash': '', 'api': ''}, 'created_by_organization': ''}
        return EdgeObject(summary)

    def get_node_type(rel_type):
        if rel_type == 'external_ref':
            return 'external_ref'
        if rel_type == 'draft':
            return 'draft'
        return 'normal'

    id_to_idx = {}

    while stack:
        depth, parent_idx, node, rel_type = stack.pop()
        node_id = node.id_
        node_type = get_node_type(rel_type)
        is_new_node = node_id not in id_to_idx
        if is_new_node:
            idx = len(nodes)
            id_to_idx[node_id] = idx
            title = node.summary.get("title", None)
            if title is None:
                title = build_title(node)
            if node_type is 'external_ref' or node_type is 'draft':
                backlinks, matches = False, False
            else:
                backlinks, matches, = backlinks_exist(node_id), matches_exist(node_id)

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
                if node_id not in hide_edge_ids:
                    for edge in node.edges:
                        try:
                            stack.append((depth + 1, idx, edge.fetch(), "edge"))
                        except EdgeError as e:
                            if e.message == edge.id_ + " not found":
                                obj = create_external_reference(edge)
                                stack.append((depth + 1, idx, obj, "external_ref"))
                                continue
                        except Exception as e:
                            raise e
            if node_id in bl_ids:
                for eoId in [val for doc in get_backlinks(node_id) for val in doc['value'].keys()]:
                    stack.append((depth + 1, idx, EdgeObject.load(eoId), "backlink"))
            if node_id in id_matches:
                for eoId in get_matches(node_id):
                    stack.append((depth + 1, idx, EdgeObject.load(eoId), "match"))

    return dict(nodes=nodes, links=links)
