import unittest
import mock
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from adapters.certuk_mod.validation.observable.hostname import HostnameValidationInfo


class HostnameValidationTests(unittest.TestCase):

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
