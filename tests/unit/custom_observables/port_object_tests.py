import unittest
from adapters.certuk_mod.builder.custom_observables.port import PortObservableDefinition


class PortObjectTypeTests(unittest.TestCase):
    NESTED_PORT_OBJECT = {
        'id': 'test_id',
        'title': 'PortObjectTest',
        'description': 'object for testing port object type',
        '_object': {
            'id': 'opensource:Port-blah-blah',
            'properties': {
                'xsi:type': 'PortObjectType',
                'port_value': {
                    'condition': 'Equals',
                    'value': 9030
                },
                'layer4_protocol': {
                    'pattern_type': 'string',
                    'is_obfuscated': True,
                    'value': 'tcp'
                },
            },
        },
    }

    FLAT_PORT_OBJECT = {
        'id': 'test_id',
        'title': 'PortObjectTest',
        'description': 'object for testing port object type',
        '_object': {
            'id': 'opensource:Port-blah-blah',
            'properties': {
                'xsi:type': 'PortObjectType',
                'port_value': 9030,
                'layer4_protocol': 'tcp',
            },
        },
    }

    summary_value = 'Port Value: 9030 , Layer 4 Protocol: tcp'

    to_draft_object = {
        'objectType': 'Port',
        'id': 'test_id',
        'id_ns': 'purple',
        'title': 'PortObjectTest',
        'description': 'object for testing port object type',
        'port_value': '9030',
        'layer4_protocol': 'tcp'
    }

    def test_summary_value_with_flat_fields(self):
        port_object = PortObservableDefinition()

        summary_value_flat_fields = PortObservableDefinition.summary_value_generator(port_object, PortObjectTypeTests.FLAT_PORT_OBJECT)

        self.assertEqual(PortObjectTypeTests.summary_value, summary_value_flat_fields)

    def test_summary_value_with_nested_fields(self):
        port_object = PortObservableDefinition()

        summary_value_nested_fields = PortObservableDefinition.summary_value_generator(port_object, PortObjectTypeTests.NESTED_PORT_OBJECT)

        self.assertEqual(PortObjectTypeTests.summary_value, summary_value_nested_fields)

    def test_to_draft_handling_with_flat_fields(self):
        port_object = PortObservableDefinition()

        to_draft_object = PortObservableDefinition.to_draft_handler(port_object, PortObjectTypeTests.FLAT_PORT_OBJECT, 'trust_group', 'load_by_id', id_ns='purple')

        self.assertEqual(to_draft_object, PortObjectTypeTests.to_draft_object)

    def test_to_draft_handler_with_nested_fields(self):
        port_object = PortObservableDefinition()

        to_draft_object = PortObservableDefinition.to_draft_handler(port_object, PortObjectTypeTests.NESTED_PORT_OBJECT, 'trust_group', 'load_by_id', id_ns='purple')

        self.assertEqual(to_draft_object, PortObjectTypeTests.to_draft_object)