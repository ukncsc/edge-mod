
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from observable import ObservableValidationInfo


class PortValidationInfo(ObservableValidationInfo):

    TYPE = 'PortObjectType'

    def __init__(self, observable_data, **field_validation):
        super(PortValidationInfo, self).__init__(PortValidationInfo.TYPE, observable_data, **field_validation)
        self.port_value = field_validation.get('port_value')

    @classmethod
    def validate(cls, **observable_data):
        port = observable_data.get('port_value')
        if port:
            port_validation = None
        else:
            port_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Port value is missing')

        return cls(observable_data, port_value=port_validation)
