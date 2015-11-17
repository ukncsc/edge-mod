import unittest
import mock
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from adapters.certuk_mod.validation.observable.hostname import HostnameValidationInfo


class HostnameValidationTests(unittest.TestCase):

    VALID_HOSTNAMES = [
        'hello',
        'blah.blah',
        'abc-123',
        'abc-123.blah.blah'
    ]

    INVALID_HOSTNAMES = [
        '-hello',
        '123.blah'
    ]

    def test_Validate_IfNoValue_Error(self):
        hostname_validation = HostnameValidationInfo.validate()
        self.assertEqual(hostname_validation.hostname_value.status, ValidationStatus.ERROR)

    @mock.patch('adapters.certuk_mod.validation.observable.hostname.HostnameValidationInfo.validate_hostname_value')
    def test_Validate_IfValueExists_CallValidateHostnameValue(self, mock_validate_hostname_value):
        hostname_value = 'dummy value'
        mock_validate_result = FieldValidationInfo(ValidationStatus.INFO, 'blah')
        mock_validate_hostname_value.return_value = mock_validate_result
        for is_domain in [True, False, None]:
            if is_domain is None:
                hostname_validation = HostnameValidationInfo.validate(hostname_value=hostname_value)
            else:
                hostname_validation = HostnameValidationInfo.validate(hostname_value=hostname_value,
                                                                      is_domain_name=is_domain)
            mock_validate_hostname_value.assert_called_with(bool(is_domain), hostname_value)
            self.assertEqual(hostname_validation.hostname_value, mock_validate_result)

    @mock.patch('adapters.certuk_mod.validation.observable.domain.DomainNameValidationInfo.get_domain_type_from_value')
    def test_ValidateHostnameValue_IfValid_Pass(self, mock_get_domain_type):
        mock_get_domain_type.return_value = 'blah'

        hostname_validation = HostnameValidationInfo.validate(is_domain_name=True, hostname_value='Dummy domain')
        self.assertIsNone(hostname_validation.hostname_value)

        for hostname in self.VALID_HOSTNAMES:
            hostname_validation = HostnameValidationInfo.validate(is_domain_name=False, hostname_value=hostname)
            self.assertIsNone(hostname_validation.hostname_value)

    @mock.patch('adapters.certuk_mod.validation.observable.domain.DomainNameValidationInfo.get_domain_type_from_value')
    def test_ValidateHostnameValue_IfInvalid_Warn(self, mock_get_domain_type):
        mock_get_domain_type.return_value = None

        hostname_validation = HostnameValidationInfo.validate(is_domain_name=True, hostname_value='Dummy domain')
        self.assertEqual(hostname_validation.hostname_value.status, ValidationStatus.WARN)

        for hostname in self.INVALID_HOSTNAMES:
            hostname_validation = HostnameValidationInfo.validate(is_domain_name=False, hostname_value=hostname)
            self.assertEqual(hostname_validation.hostname_value.status, ValidationStatus.WARN)
