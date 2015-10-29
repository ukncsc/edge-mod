
from .. import ValidationStatus, FieldValidationInfo
from .observable import ObservableValidationInfo
import socket


class AddressValidationInfo(ObservableValidationInfo):

    IPv4_CATEGORY = 'ipv4-addr'
    IPv6_CATEGORY = 'ipv6-addr'
    EMAIL_CATEGORY = 'e-mail'
    MAC_CATEGORY = 'mac'
    CIDR_CATEGORY = 'cidr'

    TYPE = 'AddressObjectType'

    def __init__(self, **field_validation):
        super(AddressValidationInfo, self).__init__(AddressValidationInfo.TYPE, **field_validation)
        self.address_value = field_validation['address_value']
        self.category = field_validation['category']

    @staticmethod
    def validate(**field_values):
        category_validation = None
        address_validation = None

        category = field_values['category']

        address_validator = AddressValidationInfo.__get_category_handler(category)
        if address_validator:
            address_validation = address_validator(field_values['address_value'])
        else:
            category_validation = FieldValidationInfo(ValidationStatus.ERROR,
                                                      'Unable to determine the address category (%s).' % category)

        return AddressValidationInfo(address_value=address_validation, category=category_validation)

    @staticmethod
    def __get_category_handler(category):
        handlers = {
            AddressValidationInfo.IPv4_CATEGORY: AddressValidationInfo.__validate_ipv4,
            AddressValidationInfo.IPv6_CATEGORY: AddressValidationInfo.__dummy_warn,
            AddressValidationInfo.EMAIL_CATEGORY: AddressValidationInfo.__dummy_error,
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

        return FieldValidationInfo(status, message)
