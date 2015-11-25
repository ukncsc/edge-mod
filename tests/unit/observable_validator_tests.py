import unittest
import mock
from adapters.certuk_mod.validation.observable.validator import ObservableValidator


class ObservableValidatorTests(unittest.TestCase):

    VALIDATION_HANDLER_PATHS = {
        'Address': 'address.Address',
        'Hostname': 'hostname.Hostname',
        'DomainName': 'domain.DomainName',
        'Mutex': 'mutex.Mutex',
        'SocketAddress': 'socket_type.Socket',
        'HTTPSession': 'http_session.HTTPSession',
        'Artifact': 'artifact.Artifact',
        'URI': 'uri.URI',
        'EmailMessage': 'email_type.Email',
        'File': 'file.File',
        'WindowsRegistryKey': 'registry_key.RegistryKey'
    }

    VALIDATOR_BASE_PATH = 'adapters.certuk_mod.validation.observable.%sValidationInfo.validate'

    def test_Validate_KnownType_CallsCorrectHandler(self):
        for object_type, validator_path in self.VALIDATION_HANDLER_PATHS.iteritems():
            with mock.patch(self.VALIDATOR_BASE_PATH % validator_path) as mock_validation_handler:
                mock_return_value = 'Dummy return value'
                mock_validation_handler.return_value = mock_return_value

                observable_properties = {
                    'object_type': '%sObjectType' % object_type,
                    'some_other_field': 'blah'
                }
                validation_result = ObservableValidator.validate(**observable_properties)

                self.assertEqual(validation_result, mock_return_value)
                mock_validation_handler.assert_called_with(**observable_properties)

    @mock.patch('adapters.certuk_mod.validation.observable.validator.ObservableValidationInfo')
    def test_Validate_UnknownType_ReturnsCorrectType(self, mock_validation_info):
        observable_properties = {
            'object_type': 'SomeRandomObjectType',
            'some_other_field': 'blah'
        }
        validation_result = ObservableValidator.validate(**observable_properties)

        self.assertEqual(validation_result, mock_validation_info.return_value)
        mock_validation_info.assert_called_with(mock_validation_info.TYPE, observable_properties)

    @mock.patch('adapters.certuk_mod.validation.observable.validator.ObservableValidationInfo')
    def test_Validate_NoType_ReturnsCorrectType(self, mock_validation_info):
        observable_properties = {
            'object_type': None,
            'some_other_field': 'blah'
        }
        validation_result = ObservableValidator.validate(**observable_properties)

        self.assertEqual(validation_result, mock_validation_info.return_value)
        mock_validation_info.assert_called_with(None, observable_properties)
