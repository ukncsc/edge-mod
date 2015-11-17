import unittest
import mock
from adapters.certuk_mod.validation.observable.uri import URIValidationInfo
from adapters.certuk_mod.validation import ValidationStatus


class URIValidationTests(unittest.TestCase):

    VALID_URNS = [
        'urn:blah:blah',
        'urn:125gb:abs@424'
        'urn:a'
    ]

    INVALID_URNS = [
        'urn',
        'abc:123'
    ]

    VALID_URLS = [
        'http://blah',
        'ftp://123.com',
        'mailto:someone@theworld.com',
        'https://some.website/someresource&=123',
        'http://blah.blah/index.php?hello'
    ]

    INVALID_URLS = [
        'blah/blah',
        '-http://abc.com',
    ]

    def test_Validate_NoType_Error(self):
        uri_validation = URIValidationInfo.validate()
        self.assertEqual(uri_validation.type.status, ValidationStatus.ERROR)

    def test_Validate_InvalidType_Error(self):
        uri_validation = URIValidationInfo.validate(type='blah')
        self.assertEqual(uri_validation.type.status, ValidationStatus.ERROR)

    def test_Validate_ValidType_Pass(self):
        for type_ in ['URL', 'General URN', 'Domain Name']:
            uri_validation = URIValidationInfo.validate(type=type_)
            self.assertIsNone(uri_validation.type)

    def test_Validate_NoValue_Error(self):
        uri_validation = URIValidationInfo.validate()
        self.assertEqual(uri_validation.value.status, ValidationStatus.ERROR)

    def test_Validate_InvalidURL_Warn(self):
        for url in self.INVALID_URLS:
            uri_validation = URIValidationInfo.validate(type='URL', value=url)
            self.assertEqual(uri_validation.value.status, ValidationStatus.WARN)

    def test_Validate_ValidURL_Pass(self):
        for url in self.VALID_URLS:
            uri_validation = URIValidationInfo.validate(type='URL', value=url)
            self.assertIsNone(uri_validation.value)

    def test_Validate_InvalidURN_Warn(self):
        for urn in self.INVALID_URNS:
            uri_validation = URIValidationInfo.validate(type='General URN', value=urn)
            self.assertEqual(uri_validation.value.status, ValidationStatus.WARN)

    def test_Validate_ValidURN_Pass(self):
        for urn in self.VALID_URNS:
            uri_validation = URIValidationInfo.validate(type='General URn', value=urn)
            self.assertIsNone(uri_validation.value)

    @mock.patch('adapters.certuk_mod.validation.observable.domain.DomainNameValidationInfo.get_domain_type_from_value')
    def test_Validate_InvalidDomain_Warn(self, mock_get_domain_type):
        mock_get_domain_type.return_value = None
        uri_validation = URIValidationInfo.validate(type='Domain Name', value='blah')
        self.assertEqual(uri_validation.value.status, ValidationStatus.WARN)

    @mock.patch('adapters.certuk_mod.validation.observable.domain.DomainNameValidationInfo.get_domain_type_from_value')
    def test_Validate_ValidDomain_Pass(self, mock_get_domain_type):
        mock_get_domain_type.return_value = 'Blah'
        uri_validation = URIValidationInfo.validate(type='Domain Name', value='blah')
        self.assertIsNone(uri_validation.value)
