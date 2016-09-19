
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from observable import ObservableValidationInfo
import re
import socket
from email.utils import parseaddr


class AddressValidationInfo(ObservableValidationInfo):

    IPv4_CATEGORY = 'ipv4-addr'
    IPv6_CATEGORY = 'ipv6-addr'
    EMAIL_CATEGORY = 'e-mail'
    MAC_CATEGORY = 'mac'
    CIDR_CATEGORY = 'cidr'

    TYPE = 'AddressObjectType'

    EMAIL_MATCHER = re.compile(
        r'^[A-Z0-9][A-Z0-9._%+-]{0,63}@(?:(?=[A-Z0-9-]{1,63}\.)[A-Z0-9]+(?:-[A-Z0-9]+)*\.){1,8}[A-Z]{2,63}$',
        re.IGNORECASE
    )
    MAC_MATCHER = re.compile(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$', re.IGNORECASE)

    WARN_IPv4_PREFIXES = [
        '192.168.',
        '172.16.',
        '10.',
        '255.',
        '8.8.'
    ]

    def __init__(self, observable_data, **field_validation):
        super(AddressValidationInfo, self).__init__(AddressValidationInfo.TYPE, observable_data, **field_validation)
        self.address_value = field_validation['address_value']
        self.category = field_validation['category']

    @classmethod
    def validate(cls, **observable_data):
        address_value = observable_data['address_value']
        category = observable_data.get('category', AddressValidationInfo.IPv4_CATEGORY) or AddressValidationInfo.IPv4_CATEGORY  #Default according to Cybox Schema

        category_validation = None
        address_validation = None

        address_validator = cls.__get_category_handler(category)
        if address_validator:
            address_validation = address_validator(address_value)
        else:
            category_validation = FieldValidationInfo(ValidationStatus.ERROR,
                                                      'Unable to determine the address category (%s)' % category)

        return cls(observable_data, address_value=address_validation, category=category_validation)

    @staticmethod
    def __get_category_handler(category):
        handlers = {
            AddressValidationInfo.IPv4_CATEGORY: AddressValidationInfo.__validate_ipv4,
            AddressValidationInfo.IPv6_CATEGORY: AddressValidationInfo.__validate_ipv6,
            AddressValidationInfo.EMAIL_CATEGORY: AddressValidationInfo.__validate_email,
            AddressValidationInfo.MAC_CATEGORY: AddressValidationInfo.__validate_mac,
            AddressValidationInfo.CIDR_CATEGORY: AddressValidationInfo.__validate_cidr
        }
        return handlers.get(category)

    @staticmethod
    def is_ipv4(address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except socket.error:  # not a valid address
            return False

        return True

    @staticmethod
    def __validate_ipv4(address):
        status = None

        if not address:
            status = FieldValidationInfo(ValidationStatus.ERROR, 'IP address is missing')
        elif AddressValidationInfo.is_ipv4(address):
            if AddressValidationInfo.__is_warning_ipv4(address):
                status = FieldValidationInfo(ValidationStatus.WARN, 'IP address appears to be private')
        else:
            status = FieldValidationInfo(ValidationStatus.WARN, 'IPv4 address appears invalid')

        return status

    @staticmethod
    def __is_warning_ipv4(valid_address):
        # Could do a regex but we've already gone to the effort of determining a valid ip
        for prefix in AddressValidationInfo.WARN_IPv4_PREFIXES:
            if valid_address.find(prefix) == 0:
                return True
        return False

    @staticmethod
    def is_ipv6(address):
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True

    @staticmethod
    def __validate_ipv6(address):
        if not address:
            return FieldValidationInfo(ValidationStatus.ERROR, 'IPv6 address value is missing')
        if not AddressValidationInfo.is_ipv6(address):
            return FieldValidationInfo(ValidationStatus.WARN, 'IPv6 address appears invalid')
        return None

    @staticmethod
    def __validate_email(address):
        if not address:
            return FieldValidationInfo(ValidationStatus.ERROR, 'Email address is missing')
        _, email_address = parseaddr(address)
        if AddressValidationInfo.EMAIL_MATCHER.match(email_address) is None:
            return FieldValidationInfo(ValidationStatus.WARN, 'The email address may be invalid')
        return None

    @staticmethod
    def __validate_mac(address):
        if not address:
            return FieldValidationInfo(ValidationStatus.ERROR, 'MAC address is missing')
        if AddressValidationInfo.MAC_MATCHER.match(address) is None:
            return FieldValidationInfo(ValidationStatus.WARN, 'MAC address may be invalid')
        return None

    @staticmethod
    def __validate_cidr(address):
        if not address:
            return FieldValidationInfo(ValidationStatus.ERROR, 'CIDR value is missing')
        address_parts = address.split('/')
        if len(address_parts) == 2:
            address_validation = AddressValidationInfo.__validate_ipv4(address_parts[0])
            if address_validation is None:
                try:
                    range_bits = int(address_parts[1])
                    if 0 <= range_bits <= 32:
                        return None
                except ValueError:
                    pass

        return FieldValidationInfo(ValidationStatus.WARN, 'CIDR value appears invalid')
