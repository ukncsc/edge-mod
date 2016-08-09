from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from hostname import HostnameValidationInfo
from observable import ObservableValidationInfo
from socket_validator import validate_protocol, validate_ip_address


class NetworkConnectionValidationInfo(ObservableValidationInfo):
    TYPE = 'NetworkConnectionObjectType'

    def __init__(self, observable_data, **field_validation):
        super(NetworkConnectionValidationInfo, self).__init__(NetworkConnectionValidationInfo.TYPE, observable_data,
                                                              **field_validation)
        self.source_socket_address = field_validation.get('source_socket_address')
        self.destination_socket_address = field_validation.get('destination_socket_address')

    @staticmethod
    def validate_socket(socket):
        protocol = socket.get('protocol')
        ip_address = socket.get('ip_address')
        hostname = socket.get('hostname')

        protocol_validation = validate_protocol(protocol)
        ip_address_validation = None
        hostname_validation = None

        if bool(ip_address) == bool(hostname):
            ip_address_validation = hostname_validation = \
                FieldValidationInfo(ValidationStatus.ERROR, 'Only one of IP address or Hostname must be completed')
        elif ip_address:
            ip_address_validation = validate_ip_address(ip_address)
        elif hostname:
            hostname_validation = HostnameValidationInfo.validate_hostname_value(False, hostname)

        return dict(protocol=protocol_validation,
                    ip_address=ip_address_validation,
                    hostname=hostname_validation)

    @classmethod
    def validate(cls, **observable_data):
        source_socket = observable_data.get('source_socket_address')
        destination_socket = observable_data.get('destination_socket_address')
        source_validation = NetworkConnectionValidationInfo.validate_socket(source_socket)
        destination_validation = NetworkConnectionValidationInfo.validate_socket(destination_socket)
        return cls(observable_data, source_socket_address_port=source_validation.get('port'),
                   source_socket_address_protocol=source_validation.get('protocol'),
                   source_socket_address_ip_address=source_validation.get('ip_address'),
                   source_socket_address_hostname=source_validation.get('hostname'),
                   destination_socket_address_port=destination_validation.get('port'),
                   destination_socket_address_protocol=destination_validation.get('protocol'),
                   destination_socket_address_ip_address=destination_validation.get('ip_address'),
                   destination_socket_address_hostname=destination_validation.get('hostname'))

