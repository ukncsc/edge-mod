from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo

from observable import ObservableValidationInfo
from socket_type import SocketValidationInfo
from hostname import HostnameValidationInfo
from address import AddressValidationInfo


class NetworkConnectionValidationInfo(ObservableValidationInfo):
    TYPE = 'NetworkConnectionObjectType'

    def __init__(self, observable_data, **field_validation):
        super(NetworkConnectionValidationInfo, self).__init__(NetworkConnectionValidationInfo.TYPE, observable_data,
                                                              **field_validation)
        self.source_socket_address = field_validation.get('source_socket_address')
        self.destination_socket_address = field_validation.get('destination_socket_address')


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
                if not (0 <= port_value <= 65535):
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
    def validate_socket(cls, observable_data):
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

        return dict(port=port_validation, protocol=protocol_validation,
                    ip_address=ip_address_validation,
                    hostname=hostname_validation)

    @classmethod
    def validate(cls, **observable_data):
        source_socket = observable_data.get('source_socket_address')
        destination_socket = observable_data.get('destination_socket_address')

        source_validation = cls.validate_socket(source_socket)
        destination_validation = cls.validate_socket(destination_socket)
        return cls(observable_data, source_socket_address_port=source_validation['port'],
                   source_socket_address_protocol=source_validation['protocol'],
                   source_socket_address_ip_address=source_validation['ip_address'],
                   source_socket_address_hostname=source_validation['hostname'],
                   destination_socket_address_port=destination_validation['port'],
                   destination_socket_address_protocol=destination_validation['protocol'],
                   destination_socket_address_ip_address=destination_validation['ip_address'],
                   destination_socket_address_hostname=destination_validation['hostname'])
