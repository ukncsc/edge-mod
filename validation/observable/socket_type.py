from observable import ObservableValidationInfo
from socket_validator import validate_socket


class SocketValidationInfo(ObservableValidationInfo):
    TYPE = 'SocketAddressObjectType'

    def __init__(self, observable_data, **field_validation):
        super(SocketValidationInfo, self).__init__(SocketValidationInfo.TYPE, observable_data, **field_validation)
        self.port = field_validation.get('port')
        self.protocol = field_validation.get('protocol')
        self.hostname = field_validation.get('hostname')
        self.ip_address = field_validation.get('ip_address')

    @classmethod
    def validate(cls, **observable_data):
        validation = validate_socket(observable_data)

        return cls(observable_data, port=validation['port'], protocol=validation['protocol'],
                   ip_address=validation['ip_address'],
                   hostname=validation['hostname'])
