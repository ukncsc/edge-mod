import unittest
import mock
from adapters.certuk_mod.builder.custom_observables.port import PortObservableDefinition


class PortObjectTypeTests(unittest.TestCase):

    def __generate_common_fields_mock():
        common_fields_mock = mock.MagicMock()
        common_fields_mock.title = 'PortObjectTest'
        common_fields_mock.id_ = "test_id"
        common_fields_mock.id_ns = "purple"
        common_fields_mock.description = 'object for testing port object type'
        common_fields_mock._object.id = 'opensource:Port-blah-blah'
        return common_fields_mock

    nested_port_object_mock = __generate_common_fields_mock()
    nested_port_object_mock._object.properties.port_value.value = 9030
    nested_port_object_mock._object.properties.layer4_protocol.value = 'tcp'

    flat_port_object_mock = __generate_common_fields_mock()
    flat_port_object_mock._object.properties.port_value = 9030
    flat_port_object_mock._object.properties.layer4_protocol = 'tcp'

    expected_summary_value = 'Port Value: 9030, Layer 4 Protocol: tcp'

    expected_to_draft_object = {
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

        summary_value_flat_fields = port_object.summary_value_generator(PortObjectTypeTests.flat_port_object_mock)

        self.assertEqual(PortObjectTypeTests.expected_summary_value, summary_value_flat_fields)

    def test_summary_value_with_nested_fields(self):
        port_object = PortObservableDefinition()

        summary_value_nested_fields = port_object.summary_value_generator(PortObjectTypeTests.nested_port_object_mock)

        self.assertEqual(PortObjectTypeTests.expected_summary_value, summary_value_nested_fields)

    def test_to_draft_handling_with_flat_fields(self):
        port_object = PortObservableDefinition()

        to_draft_object = port_object.to_draft_handler(PortObjectTypeTests.flat_port_object_mock, 'trust_group', 'load_by_id', id_ns='purple')

        self.assertEqual(to_draft_object, PortObjectTypeTests.expected_to_draft_object)

    def test_to_draft_handler_with_nested_fields(self):
        port_object = PortObservableDefinition()

        to_draft_object = port_object.to_draft_handler(PortObjectTypeTests.nested_port_object_mock, 'trust_group', 'load_by_id', id_ns='purple')

        self.assertEqual(to_draft_object, PortObjectTypeTests.expected_to_draft_object)