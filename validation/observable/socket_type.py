
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from observable import ObservableValidationInfo
from address import AddressValidationInfo
from hostname import HostnameValidationInfo


class SocketValidationInfo(ObservableValidationInfo):

    TYPE = 'SocketAddressObjectType'

    def __init__(self, **field_validation):
        super(SocketValidationInfo, self).__init__(SocketValidationInfo.TYPE, **field_validation)

    @staticmethod
    def __validate_port(port):
        port_validation = None

        if port is None:
            port_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Port value is missing')
        else:
            try:
                port_value = int(port)
            except ValueError:
                port_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Invalid port value')
            else:
                if not (0 < port_value <= 65535):
                    port_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Port value outside valid range')
                elif port_value == 0:
                    port_validation = FieldValidationInfo(ValidationStatus.WARN, 'Port value is zero')

        return port_validation

    @staticmethod
    def __validate_protocol(protocol):
        protocol_validation = None

        if protocol and any(char.isdigit() for char in protocol):
            protocol_validation = FieldValidationInfo(ValidationStatus.WARN, 'Protocol contains numeric characters')

        return protocol_validation

    @staticmethod
    def __validate_ip_address(address):
        if AddressValidationInfo.is_ipv4(address) or AddressValidationInfo.is_ipv6(address):
            return None
        return FieldValidationInfo(ValidationStatus.WARN, 'Socket IP address appears invalid')

    @classmethod
    def validate(cls, **observable_data):
        port = observable_data.get('port')
        protocol = observable_data.get('protocol')
        ip_address = observable_data.get('ip_address')
        hostname = observable_data.get('hostname')

        port_validation = cls.__validate_port(port)
        protocol_validation = cls.__validate_protocol(protocol)
        ip_address_validation = None
        hostname_validation = None

        if bool(ip_address) == bool(hostname):
            ip_address_validation = hostname_validation = \
                FieldValidationInfo(ValidationStatus.ERROR, 'Only one of IP address or Hostname must be completed')
        elif ip_address:
            ip_address_validation = cls.__validate_ip_address(ip_address)
        elif hostname:
            hostname_validation = HostnameValidationInfo.validate_hostname_value(False, hostname)

        return cls(port=port_validation, protocol=protocol_validation, ip_address=ip_address_validation,
                   hostname=hostname_validation, description=observable_data.get('description'))
