import unittest
import mock
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from adapters.certuk_mod.validation.observable.socket_type import SocketValidationInfo


class SocketValidationTests(unittest.TestCase):

    def test_Validate_IfNoPort_Error(self):
        socket_validation = SocketValidationInfo.validate()
        self.assertEqual(socket_validation.port.status, ValidationStatus.ERROR)

    def test_Validate_IfPortNotInteger_Error(self):
        socket_validation = SocketValidationInfo.validate(port='blah')
        self.assertEqual(socket_validation.port.status, ValidationStatus.ERROR)

    def test_Validate_IfPortOutsideRange_Error(self):
        socket_validation = SocketValidationInfo.validate(port=-1)
        self.assertEqual(socket_validation.port.status, ValidationStatus.ERROR)

        socket_validation = SocketValidationInfo.validate(port=65536)
        self.assertEqual(socket_validation.port.status, ValidationStatus.ERROR)

    def test_Validate_IfPortIsZero_Warn(self):
        socket_validation = SocketValidationInfo.validate(port=0)
        self.assertEqual(socket_validation.port.status, ValidationStatus.WARN)

    def test_Validate_IfPortValid_Pass(self):
        socket_validation = SocketValidationInfo.validate(port=1234)
        self.assertIsNone(socket_validation.port)

    def test_Validate_IfNoHostnameAndNoIPAddress_Error(self):
        socket_validation = SocketValidationInfo.validate()
        self.assertEqual(socket_validation.hostname.status, ValidationStatus.ERROR)
        self.assertEqual(socket_validation.ip_address.status, ValidationStatus.ERROR)

    def test_Validate_IfBothHostnameAndIPAddress_Error(self):
        socket_validation = SocketValidationInfo.validate(hostname='something', ip_address='something else')
        self.assertEqual(socket_validation.hostname.status, ValidationStatus.ERROR)
        self.assertEqual(socket_validation.ip_address.status, ValidationStatus.ERROR)

    @mock.patch('adapters.certuk_mod.validation.observable.hostname.HostnameValidationInfo.validate_hostname_value')
    def test_Validate_IfHostname_CallValidateHostnameValue(self, mock_hostname_validator):
        mock_hostname_validator.return_value = FieldValidationInfo(ValidationStatus.INFO, 'Testing function call...')
        hostname_value = 'blah'

        socket_validation = SocketValidationInfo.validate(hostname=hostname_value)
        self.assertEqual(socket_validation.hostname, mock_hostname_validator.return_value)
        mock_hostname_validator.assert_called_with(False, hostname_value)

    def test_Validate_IfProtocolContainsNumeric_Warn(self):
        socket_validation = SocketValidationInfo.validate(protocol='TCP/1P')
        self.assertEqual(socket_validation.protocol.status, ValidationStatus.WARN)

    def test_Validate_IfNoProtocol_Pass(self):
        socket_validation = SocketValidationInfo.validate()
        self.assertIsNone(socket_validation.protocol)
