import inspect

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_ID
from edge.inbox import InboxProcessorForBuilders
from stix.common.kill_chains import KillChainPhaseReference, KillChainPhasesReference
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
    InboxProcessorForBuilders.add = add
