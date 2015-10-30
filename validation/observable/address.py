
from .. import ValidationStatus, FieldValidationInfo
from .observable import ObservableValidationInfo
import re
import socket


class AddressValidationInfo(ObservableValidationInfo):

    IPv4_CATEGORY = 'ipv4-addr'
    IPv6_CATEGORY = 'ipv6-addr'
    EMAIL_CATEGORY = 'e-mail'
    MAC_CATEGORY = 'mac'
    CIDR_CATEGORY = 'cidr'

    TYPE = 'AddressObjectType'

    EMAIL_MATCHER = re.compile(r'^[a-z0-9]+@[a-z]+.[a-z]+$', re.IGNORECASE)

    WARN_IPv4_PREFIXES = [
        '192.168.',
        '172.16.',
        '10.',
        '255.',
        '8.8.'
    ]

    def __init__(self, **field_validation):
        super(AddressValidationInfo, self).__init__(AddressValidationInfo.TYPE, **field_validation)
        self.address_value = field_validation['address_value']
        self.category = field_validation['category']

    @staticmethod
    def validate(**field_values):
        address_value = field_values['address_value']
        if isinstance(address_value, dict):
            address_value = address_value['value']

        return AddressValidationInfo.__validate(address_value=address_value, category=field_values['category'])

    @staticmethod
    def __validate(address_value, category):
        category_validation = None
        address_validation = None

        address_validator = AddressValidationInfo.__get_category_handler(category)
        if address_validator:
            address_validation = address_validator(address_value)
        else:
            category_validation = FieldValidationInfo(ValidationStatus.ERROR,
                                                      'Unable to determine the address category (%s).' % category)

        return AddressValidationInfo(address_value=address_validation, category=category_validation)

    @staticmethod
    def __get_category_handler(category):
        handlers = {
            AddressValidationInfo.IPv4_CATEGORY: AddressValidationInfo.__validate_ipv4,
            AddressValidationInfo.IPv6_CATEGORY: AddressValidationInfo.__validate_ipv6,
            AddressValidationInfo.EMAIL_CATEGORY: AddressValidationInfo._validate_email,
            AddressValidationInfo.MAC_CATEGORY: AddressValidationInfo.__dummy_warn,
            AddressValidationInfo.CIDR_CATEGORY: AddressValidationInfo.__dummy_error
        }
        return handlers.get(category)

    @staticmethod
    def __dummy_error(address):
        return FieldValidationInfo(ValidationStatus.ERROR, 'Computer says no.')

    @staticmethod
    def __dummy_warn(address):
        return FieldValidationInfo(ValidationStatus.WARN, 'Computer says not sure.')

    @staticmethod
    def __validate_ipv4(address):
        status = ValidationStatus.OK
        message = ''

        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                status = ValidationStatus.ERROR
            else:
                if address.count('.') != 3:
                    status = ValidationStatus.ERROR
        except socket.error:  # not a valid address
            status = ValidationStatus.ERROR

        if status == ValidationStatus.ERROR:
            message = 'Address is not a valid IPv4 address.'

        if status == ValidationStatus.OK and AddressValidationInfo.__is_warning_ipv4(address):
            status = ValidationStatus.WARN
            message = 'The IP address appears private.'

        return FieldValidationInfo(status, message)

    @staticmethod
    def __is_warning_ipv4(valid_address):
        # Could do a regex but we've already gone to the effort of determining a valid ip
        for prefix in AddressValidationInfo.WARN_IPv4_PREFIXES:
            if valid_address.find(prefix) == 0:
                return True
        return False

    @staticmethod
    def __validate_ipv6(address):
        if not address:
            return FieldValidationInfo(ValidationStatus.ERROR, 'IPv6 address value is missing.')
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return FieldValidationInfo(ValidationStatus.WARN, 'IPv6 address appears invalid.')
        return FieldValidationInfo(ValidationStatus.OK, '')

    @staticmethod
    def _validate_email(address):
        if AddressValidationInfo.EMAIL_MATCHER.match(address) is None:
            return FieldValidationInfo(ValidationStatus.WARN, 'The email address may be invalid.')
        return FieldValidationInfo(ValidationStatus.OK, '')
