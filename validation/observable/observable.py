
from .. import FieldValidationInfo, ObjectValidationInfo, ValidationStatus


class ObservableValidationInfo(ObjectValidationInfo):

    def __init__(self, observable_type, **field_validation):
        super(ObservableValidationInfo, self).__init__(**field_validation)
        self.observable_type = observable_type

    @staticmethod
    def validate(**observable_data):
        observable_type = observable_data['object_type']

        if observable_type.field_value:
            status = ValidationStatus.WARN
            message = 'Unrecognizable observable type of %s.' % observable_type.field_value
        else:
            status = ValidationStatus.OK
            message = 'Missing observable type.'

        type_validation = FieldValidationInfo(status=status,
                                              message=message,
                                              field_path_name=observable_type.field_path_name)

        return ObservableValidationInfo(observable_type, object_type=type_validation)
