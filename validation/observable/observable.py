from adapters.certuk_mod.validation import FieldValidationInfo, ObjectValidationInfo, ValidationStatus


class ObservableValidationInfo(ObjectValidationInfo):

    TYPE = 'UNKNOWN'

    def __init__(self, observable_type, observable_field_values, **field_validation):
        field_validation.update({
            'object_type': ObservableValidationInfo.__validate_type(observable_type),
            'description': ObservableValidationInfo.__validate_description(observable_field_values.get('description'))
        })
        super(ObservableValidationInfo, self).__init__(**field_validation)

        self.object_type = field_validation.get(r'object_type')
        self.description = field_validation.get(r'description')

        self.observable_field_values = observable_field_values

    @classmethod
    def validate(cls, **observable_data):
        raise NotImplementedError('This method must be overridden')

    @staticmethod
    def __validate_description(description):
        if not description:
            return FieldValidationInfo(status=ValidationStatus.INFO, message='No description')
        return None

    @staticmethod
    def __validate_type(observable_type):
        actual_type = getattr(observable_type, 'field_value', observable_type)
        field_path_name = getattr(observable_type, 'field_path_name', None)

        if not actual_type:
            return FieldValidationInfo(ValidationStatus.ERROR, 'Missing observable type', field_path_name)
        elif actual_type == ObservableValidationInfo.TYPE:
            return FieldValidationInfo(ValidationStatus.WARN, 'Unrecognizable observable type', field_path_name)
        else:
            return None
