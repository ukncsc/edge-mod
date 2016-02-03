import inspect

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_ID
from edge.inbox import InboxProcessorForBuilders
from stix.common.kill_chains import KillChainPhaseReference, KillChainPhasesReference
from signalregistry import SignalRegistry
from mongoengine.connection import get_db
from edge.inbox import InboxError, InboxProcessor
from edge import LOCAL_NAMESPACE, LOCAL_ALIAS


def get_previous_frame():
    return inspect.stack()[2]


def frame_is_publish_indicator(frame):
    return frame[3] == 'publish_indicator'


def add_kill_chain_phase_reference_data_from_frame(api_object, frame):
    indicator = api_object.obj
    indicator_builder_data = frame[0].f_locals['indicator_data']
    kill_chain_phase_id = indicator_builder_data.get('kill_chain_phase')
    if kill_chain_phase_id:
        kill_chain_phase = KillChainPhaseReference(kill_chain_id=KILL_CHAIN_ID, phase_id=kill_chain_phase_id)
        indicator._object.kill_chain_phases = KillChainPhasesReference([kill_chain_phase])
    return api_object


def add(self, inbox_item):
    api_object = inbox_item.api_object
    if api_object.ty == 'ind':
        frame = get_previous_frame()
        try:
            if frame_is_publish_indicator(frame):
                inbox_item.api_object = add_kill_chain_phase_reference_data_from_frame(api_object, frame)
        finally:
            del frame

    super(InboxProcessorForBuilders, self).add(inbox_item)


def get_objects(content, db):
    query = {
        '_id': {
            '$in': content
        }
    }
    projection = {
        'data.edges': 1,
        'data.api.timestamp': 1,
        'data.summary.type': 1,
        'type': 1,
        'created_on': 1
    }
    return {doc['_id']: doc for doc in db.stix.find(query, projection)}


def update_non_observables(top_level_objects, db):
    from dateutil.parser import parse as date_time_parse

    for _id in top_level_objects:
        doc = top_level_objects[_id]
        if doc['type'] != 'obs':
            actual_date = doc['data']['api'].get('timestamp', {})
            if actual_date:
                # Update the created_on date:
                actual_date = date_time_parse(actual_date)
                # The saved 'created_on' dates are UTC, but technically aren't offset-aware...
                # However, parsing a string returns an offset-aware datetime object, which we won't be able to compare
                #  with offset-naive datetimes....
                # So let's derive the offset from UTC, subtract it from the hour, then remove the timezone info...
                # ffs
                actual_date = (actual_date - actual_date.tzinfo.utcoffset(actual_date)).replace(tzinfo=None)
                db.stix.update({
                    '_id': _id
                }, {
                    '$set': {
                        'created_on': actual_date
                    }
                })
                doc['created_on'] = actual_date


def update_observables_date(children, top_level, db):
    db.stix.update({
        '_id': {
            '$in': children
        }
    }, {
        '$set': {
            'created_on': top_level['created_on']
        }
    }, multi=True)


def update_observables(top_level_objects, observables, db):
    # Inspect the children of all top-level objects... for those that are observables (and that are in scope here),
    #  update their 'created_on' dates to that of the top-level object...
    for _id in top_level_objects:
        top_level = top_level_objects[_id]
        if top_level['type'] != 'pkg':
            for edge_id in top_level['data']['edges']:
                if edge_id in observables:
                    current_obs = observables[edge_id]
                    # Observable compositions can have child observables/observable compositions, so we need to explore
                    # the entire tree...
                    queue = [current_obs]
                    all_obs_children = [edge_id] if top_level['created_on'] < current_obs['created_on'] else []
                    while len(queue):
                        obs = queue.pop()
                        obs_edge_ids = [edge_id for edge_id in obs.get('data', {}).get('edges', {}) if
                                        edge_id in observables and edge_id not in all_obs_children and top_level[
                                            'created_on'] < observables[edge_id]['created_on']]
                        # This guards against duplicate references, but should never happen...
                        obs_edge_ids = list(set(obs_edge_ids))

                        all_obs_children.extend(obs_edge_ids)

                        queue.extend([observables[_id] for _id in obs_edge_ids])

                    # Finally update the observables' date:
                    if all_obs_children:
                        update_observables_date(all_obs_children, top_level, db)
                    # ...and locally...
                    for obs_id, obs in observables.iteritems():
                        if obs_id in all_obs_children:
                            obs['created_on'] = top_level['created_on']


def update_created_on(content, user, txn_id, **kwargs):

    db = get_db()

    objects = get_objects(content, db)

    top_level_objects = {_id: objects[_id] for _id in objects if objects[_id]['type'] != 'obs'}

    update_non_observables(top_level_objects, db)

    observables = {
        _id: objects[_id] for _id in objects if objects[_id]['type'] == 'obs'
    }

    update_observables(top_level_objects, observables, db)

old_inbox_add = InboxProcessor.add


def name_space_check(self, inbox_item):
    api_object = inbox_item.api_object
    if api_object.id_.startswith(LOCAL_ALIAS + ":") \
            and api_object.obj.id_ns != LOCAL_NAMESPACE:
        raise InboxError(
            "'%s' starts with the local STIX alias '%s', "
            "but uses the namespace '%s' rather than the local STIX namespace '%s'"
                % (api_object.id_, LOCAL_ALIAS, api_object.obj.id_ns, LOCAL_NAMESPACE))
    old_inbox_add(self, inbox_item)

InboxProcessor.add = name_space_check


def apply_patch():
    SignalRegistry().signal('inbox.post-merge').connect(update_created_on)
    InboxProcessorForBuilders.add = add
