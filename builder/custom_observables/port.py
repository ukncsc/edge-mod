from cybox.objects.port_object import Port

from edge.tools import rgetattr
from adapters.certuk_mod.builder.custom_observable_definition import CustomObservableDefinition
from adapters.certuk_mod.builder.custom_observables.custom_observable_utils import collapse_nested_values


class PortObservableDefinition(CustomObservableDefinition):

    def __init__(self):
        super(PortObservableDefinition, self).__init__(
            object_type='PortObjectType',
            human_readable_type='Port',
            can_batch_create=False,
            custom_id_prefix='port'
        )

    def builder_to_stix_object(self, object_data):
        port = Port()
        port.port_value = object_data.get('port_value')
        port.layer4_protocol = object_data.get('layer4_protocol')

        return port

    def summary_value_generator(self, obj):
        flat_port_value = str(collapse_nested_values(rgetattr(obj, ['_object', 'properties', 'port_value'])))
        flat_layer4_protocol = str(collapse_nested_values(rgetattr(obj, ['_object', 'properties', 'layer4_protocol'])))

        return str("Port Value: " + flat_port_value + ", Layer 4 Protocol: " + flat_layer4_protocol)

    def to_draft_handler(self, observable, tg, load_by_id, id_ns=''):
        return {
            'objectType': 'Port',
            'id': rgetattr(observable, ['id_'], ''),
            'id_ns': id_ns,
            'title': rgetattr(observable, ['title'], ''),
            'description': str(rgetattr(observable, ['description'], '')),
            'port_value': str(collapse_nested_values(rgetattr(observable, ['_object', 'properties', 'port_value']))),
            'layer4_protocol': str(collapse_nested_values(rgetattr(observable,['_object', 'properties', 'layer4_protocol'])))
        }


