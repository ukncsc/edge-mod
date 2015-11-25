import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.address import AddressValidationInfo


class AddressValidationTests(unittest.TestCase):

    INVALID_CATEGORIES = [
        'ip-addr',
        '',
        None
    ]

    VALID_ADDRESSES = {
        'ipv4-addr': ('122.234.201.2',),
        'ipv6-addr': ('2001:db8:85a3::8a2e:370:7334', '2001:0db8:85a3:0000:0000:8a2e:0370:7334'),
        'e-mail': ('mr.paul@purple.com', 'Admin <admin@company.com>'),
        'mac': ('01:23:45:67:89:ab', '01-23-45-67-89-AB'),
        'cidr': ('125.230.156.0/24',)
    }

    INVALID_ADDRESSES = {
        'ipv4-addr': ('122.234.201.02', '256.221.102.3', '122.e32.201.0'),
        'ipv6-addr': ('2001:db8:85a3:::8a2e:370:7334', '2001:0db8:85g3:0000:0000:8a2e:0370:7334'),
        'e-mail': ('test@test', 'test', '-mr.paul@purple.com', 'abc@@xyz', 'hi@123'),
        'mac': ('01::23:45:67:89:ab', '01:23:45:67:89:xy', '01-23-45-67-89-XY', '01--23-45-67-89-XY',
                '01-23-45-67-89-01-02'),
        'cidr': ('125.230.156.0/37', '125.260.156.0/27', '1/24', '203.154.165.0/x')
    }

    PRIVATE_ADDRESSES = [
        '192.168.0.1',
        '10.0.2.15',
        '172.16.235.1',
        '8.8.0.1',
        '255.255.0.0'
    ]

    def test_Validate_IfNoValidCategory_Fails(self):
        for category in self.INVALID_CATEGORIES:
            address_validation = AddressValidationInfo.validate(category=category, address_value=None)
            self.assertEqual(address_validation.category.status, ValidationStatus.ERROR)

    def test_Validate_IfNoAddressValue_Fails(self):
        for category in ['ipv4-addr', 'ipv6-addr', 'e-mail', 'mac', 'cidr']:
            address_validation = AddressValidationInfo.validate(category=category, address_value=None)
            self.assertEqual(address_validation.address_value.status, ValidationStatus.ERROR)

    def test_Validate_IfValidAddress_Passes(self):
        for category in self.VALID_ADDRESSES:
            for address in self.VALID_ADDRESSES[category]:
                address_validation = AddressValidationInfo.validate(category=category, address_value=address)
                self.assertIsNone(address_validation.category,
                                  'Expecting category validation for %s/%s to be None' % (category, address))
                self.assertIsNone(address_validation.address_value,
                                  'Expecting address_value validation for %s/%s to be None' % (category, address))

    def test_Validate_IfValidPrivateAddress_PassesAndWarns(self):
        for address in self.PRIVATE_ADDRESSES:
            address_validation = AddressValidationInfo.validate(category='ipv4-addr', address_value=address)
            self.assertEqual(address_validation.address_value.status, ValidationStatus.WARN)

    def test_Validate_IfInvalidAddress_Warns(self):
        for category in self.INVALID_ADDRESSES:
            for address in self.INVALID_ADDRESSES[category]:
                address_validation = AddressValidationInfo.validate(category=category, address_value=address)
                self.assertIsNone(address_validation.category,
                                  'Expecting category validation for %s/%s to be None' % (category, address))
                self.assertEqual(address_validation.address_value.status, ValidationStatus.WARN,
                                 'Expecting address_value validation for %s/%s to be WARN' % (category, address))
