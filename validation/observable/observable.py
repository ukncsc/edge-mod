
from .. import FieldValidationInfo, ObjectValidationInfo, ValidationStatus, FieldAlias


class ObservableValidationInfo(ObjectValidationInfo):

    def __init__(self, observable_type, description=None, unknown_type=False, **field_validation):
        self.observable_type = observable_type
        common_validation = ObservableValidationInfo.__validate_common_fields(object_type=observable_type,
                                                                              description=description,
                                                                              unknown_type=unknown_type)
        field_validation.update(common_validation)
        super(ObservableValidationInfo, self).__init__(**field_validation)

    @staticmethod
    def validate(**observable_data):
        return ObservableValidationInfo(**observable_data)

    @staticmethod
    def __validate_common_fields(**observable_data):
        observable_type = observable_data['object_type']
        actual_type = observable_type.field_value if isinstance(observable_type, FieldAlias) else observable_type

        type_status = ValidationStatus.OK
        type_message = ''

        if observable_data.get('unknown_type', False):
            type_status = ValidationStatus.WARN
            type_message = 'Unrecognizable observable type of %s.' % actual_type
        elif not actual_type:
            type_status = ValidationStatus.ERROR
            type_message = 'Missing observable type.'

        type_validation = FieldValidationInfo(status=type_status,
                                              message=type_message,
                                              field_path_name=getattr(observable_type, 'field_path_name', None))

        description_validation = None
        if not observable_data.get('description'):
            description_validation = FieldValidationInfo(status=ValidationStatus.INFO, message='No description.')

        return {
            'object_type': type_validation,
            'description': description_validation
        }
