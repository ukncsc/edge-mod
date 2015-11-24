import inspect

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_ID
from edge.inbox import InboxProcessorForBuilders
from stix.common.kill_chains import KillChainPhaseReference, KillChainPhasesReference


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


def apply_patch():
    InboxProcessorForBuilders.add = add
