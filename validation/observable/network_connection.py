from observable import ObservableValidationInfo
from socket_validator import validate_socket


class NetworkConnectionValidationInfo(ObservableValidationInfo):
    TYPE = 'NetworkConnectionObjectType'

    def __init__(self, observable_data, **field_validation):
        super(NetworkConnectionValidationInfo, self).__init__(NetworkConnectionValidationInfo.TYPE, observable_data,
                                                              **field_validation)
        self.source_socket_address = field_validation.get('source_socket_address')
        self.destination_socket_address = field_validation.get('destination_socket_address')

    @classmethod
    def validate(cls, **observable_data):
        source_socket = observable_data.get('source_socket_address')
        destination_socket = observable_data.get('destination_socket_address')

        source_validation = validate_socket(source_socket)
        destination_validation = validate_socket(destination_socket)
        return cls(observable_data, source_socket_address_port=source_validation['port'],
                   source_socket_address_protocol=source_validation['protocol'],
                   source_socket_address_ip_address=source_validation['ip_address'],
                   source_socket_address_hostname=source_validation['hostname'],
                   destination_socket_address_port=destination_validation['port'],
                   destination_socket_address_protocol=destination_validation['protocol'],
                   destination_socket_address_ip_address=destination_validation['ip_address'],
                   destination_socket_address_hostname=destination_validation['hostname'])
