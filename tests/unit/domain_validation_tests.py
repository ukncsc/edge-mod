import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.domain import DomainNameValidationInfo


class DomainValidationTests(unittest.TestCase):

    VALID_DOMAINS = {
        'TLD': ('.com', '.uk', 'gov'),
        'FQDN': ('abc.com', '123.com', 'www.abc.co.uk')
    }

    INVALID_DOMAINS = {
        'TLD': ('.co.uk', 'gov.uk', 'c0m'),
        'FQDN': ('-abc.com', 'test-.co.uk', 'abc.c0m')
    }

    def test_Validate_IfValueButNoType_Error(self):
        domain_validation = DomainNameValidationInfo.validate(value='.com')
        self.assertEqual(domain_validation.type.status if domain_validation.type else None,
                         ValidationStatus.ERROR)
        self.assertIsNone(domain_validation.value)

    def test_Validate_IfValidTypeButNoValue_Error(self):
        for domain_type in self.VALID_DOMAINS:
            domain_validation = DomainNameValidationInfo.validate(type=domain_type)
            self.assertEqual(domain_validation.value.status if domain_validation.value else None,
                             ValidationStatus.ERROR)
            self.assertIsNone(domain_validation.type)

    def test_Validate_IfValidTypeButInvalidValue_Warn(self):
        for domain_type in self.INVALID_DOMAINS:
            for domain_value in self.INVALID_DOMAINS[domain_type]:
                domain_validation = DomainNameValidationInfo.validate(type=domain_type, value=domain_value)
                self.assertEqual(
                    domain_validation.value.status if domain_validation.value else None, ValidationStatus.WARN,
                    'Unexpected validation (%s) with type/value: %s/%s' % (
                        domain_validation.value, domain_type, domain_value
                    )
                )
                self.assertIsNone(domain_validation.type)

    def test_Validate_IfInvalidType_Error(self):
        domain_validation = DomainNameValidationInfo.validate(type='xxx')
        self.assertEqual(domain_validation.value.status if domain_validation.value else None, ValidationStatus.ERROR)
        self.assertEqual(domain_validation.type.status if domain_validation.type else None, ValidationStatus.ERROR)

        domain_validation = DomainNameValidationInfo.validate(type='xxx', value='-')
        self.assertIsNone(domain_validation.value)
        self.assertEqual(domain_validation.type.status if domain_validation.type else None, ValidationStatus.ERROR)

    def test_Validate_IfValidTypeAndValue_Pass(self):
        for domain_type in self.VALID_DOMAINS:
            for domain_value in self.VALID_DOMAINS[domain_type]:
                domain_validation = DomainNameValidationInfo.validate(type=domain_type, value=domain_value)
                self.assertIsNone(domain_validation.value,
                                  'Expected no value validation info, got %s with type/value %s/%s'
                                  % (domain_validation.value, domain_type, domain_value))
                self.assertIsNone(domain_validation.type,
                                  'Expected no value validation info, got %s with type/value %s/%s'
                                  % (domain_validation.type, domain_type, domain_value))
