import hashlib
from users.models import Draft
from edge.generic import EdgeObject
from adapters.certuk_mod.visualiser.graph import create_graph, REL_TYPE_EDGE, REL_TYPE_DRAFT, REL_TYPE_EXT, \
    create_external_reference_from_id

DRAFT_ID_SEPARATOR = ":draft:"


def summarise_draft_observable(d):
    result = ""
    for key, value in d.iteritems():
        if isinstance(value, dict):
            result += " " + summarise_draft_observable(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result += " " + summarise_draft_observable(item)
                else:
                    result += " " + str(item)
        elif value and value != 'None' \
                and key != 'id' \
                and key != 'id_ns' \
                and key != 'objectType' \
                and key != 'description':

            if isinstance(value, str):
                result += value.decode('utf-8')
            elif isinstance(value, unicode):
                result += value
    return result


def observable_to_name(observable, is_draft):
    if is_draft:
        return observable['title']
    return observable['id']


def create_draft_obs_hash(obs):
    return hashlib.md5(obs['title'].encode("utf-8")).hexdigest()


def iterate_draft(draft_object, bl_ids, id_matches, hide_edge_ids, show_edge_ids, hidden_ids, request):
    def create_draft_observable_id(obs):
        d = create_draft_obs_hash(obs)
        return draft_object['id'].replace('indicator', 'observable') + DRAFT_ID_SEPARATOR + d

    def create_draft_obs_node(obs_id, title):
        summary = {'title': title, 'type': 'obs', 'value': '', '_id': obs_id, 'cv': '', 'tg': '',
                   'data': {'idns': '', 'etlp': '', 'summary': {'title': title},
                            'hash': '', 'api': ''}, 'created_by_organization': ''}
        return EdgeObject(summary)

    def create_draft_ind_node(ind_id, title):
        summary = {'title': title, 'type': 'ind', 'value': '', '_id': ind_id, 'cv': '', 'tg': '',
                   'data': {'idns': '', 'etlp': '', 'summary': {'title': title},
                            'hash': '', 'api': ''}, 'created_by_organization': ''}
        return EdgeObject(summary)

    stack = []
    for i in xrange(len(draft_object['observables'])):
        observable = draft_object['observables'][i]
        obs_id = observable.get('id', create_draft_observable_id(observable))
        if obs_id not in hidden_ids:
            if DRAFT_ID_SEPARATOR in obs_id:
                stack.append(
                    (1, 0, create_draft_obs_node(obs_id, observable_to_name(observable, True)), REL_TYPE_DRAFT))
            else:
                try:
                    stack.append((1, 0, EdgeObject.load(obs_id, request.user.filters()), REL_TYPE_EDGE))
                except:
                    stack.append((1, 0, create_external_reference_from_id(obs_id), REL_TYPE_EXT))

    stack.append((0, None, create_draft_ind_node(draft_object['id'], draft_object['title']), REL_TYPE_DRAFT))

    return create_graph(stack, bl_ids, id_matches, hide_edge_ids, show_edge_ids, hidden_ids, request)


def merge_draft_file_observables(draft_obs_offsets, draft_ind, hash_types):
    draft_obs = [draft_ind['observables'][draft_offset] for draft_offset in draft_obs_offsets]

    obs_to_keep = draft_obs[0]
    obs_to_dump = draft_obs[1:]
    for draft_ob in obs_to_dump:
        if draft_ob.get('description'):
            obs_to_keep['description'] = obs_to_keep.get('description', '') + " & " + draft_ob['description']
        if draft_ob['file_name']:
            obs_to_keep['file_name'] = draft_ob['file_name']
        for hash_type in hash_types:
            hash_value = [hash_['hash_value'] for hash_ in draft_ob['hashes'] if hash_['hash_type'] == hash_type]
            if hash_value:
                obs_to_keep['hashes'].append({'hash_type': hash_type, 'hash_value': hash_value[0]})

    obs_to_keep['title'] = ''
    obs_to_keep['title'] = summarise_draft_observable(obs_to_keep)
    draft_ind['observables'] = [obs for obs in draft_ind['observables'] if obs not in obs_to_dump]


def can_merge_observables(draft_obs_offsets, draft_ind, hash_types):
    if len(draft_obs_offsets) <= 1:
        return False, "Unable to merge these observables, at least 2 draft observables should be selected for a merge"

    if -1 in draft_obs_offsets:
        return False, "Unable to merge these observables, unable to find at least one of the observables requested"

    draft_obs = [draft_ind['observables'][draft_offset] for draft_offset in draft_obs_offsets]

    types = {draft_ob['objectType'] for draft_ob in draft_obs}
    if len(types) == 0 or (len(types) == 1 and 'File' not in types) or len(types) != 1:
        return False, "Unable to merge these observables, merge is only supported by 'File' type observables"

    file_names = {draft_ob['file_name'] for draft_ob in draft_obs if draft_ob['file_name']}
    if len(file_names) > 1:
        return False, "Unable to merge these observables, multiple observables with file names selected"

    for hash_type in hash_types:
        hash_values = []
        for draft_ob in draft_obs:
            hash_values.extend([hash_['hash_value'] for hash_ in draft_ob['hashes'] if hash_['hash_type'] == hash_type])
        if len(set(hash_values)) > 1:
            return False, "Unable to merge these observables, multiple hashes of type '" + hash_type + "' selected"
    return True, ""


def delete_observables(draft_obs_offsets, draft_ind):
    obs_to_dump = [draft_ind['observables'][draft_offset] for draft_offset in draft_obs_offsets
                   if len(draft_ind['observables']) > draft_offset >= 0]
    draft_ind['observables'] = [obs for obs in draft_ind['observables'] if obs not in obs_to_dump]


def move_observables(draft_obs_offsets, source_draft_ind, target_draft_ind):
    obs_to_move = [source_draft_ind['observables'][draft_offset] for draft_offset in draft_obs_offsets
                   if len(source_draft_ind['observables']) > draft_offset >= 0]

    target_draft_ind['observables'].extend(obs_to_move);
    source_draft_ind['observables'] = [obs for obs in source_draft_ind['observables'] if obs not in obs_to_move]


def get_draft_obs(obs_node_id, user):
    ind_id = ':'.join(obs_node_id.split(':')[0:2]).replace('observable', 'indicator')
    draft_ind = Draft.load(ind_id, user)
    obs_offset = get_draft_obs_offset(draft_ind, obs_node_id)
    return draft_ind['observables'][int(obs_offset)]


def get_draft_obs_offset(draft_ind, id_):
    hash_ = id_.split(':')[-1]
    for i in xrange(len(draft_ind['observables'])):
        obs = draft_ind['observables'][i]
        if create_draft_obs_hash(obs) == hash_:
            return i
    return -1
