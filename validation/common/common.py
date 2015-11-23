
from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus, ObjectValidationInfo


class CommonValidationInfo(ObjectValidationInfo):

    def __init__(self, **field_validation):
        super(CommonValidationInfo, self).__init__(**field_validation)
        self.tlp = field_validation.get(r'tlp')

    @classmethod
    def validate(cls, **common_data):
        field_validation = {}
        if not common_data.get(r'tlp'):
            field_validation[r'tlp'] = FieldValidationInfo(ValidationStatus.ERROR, r'TLP missing')
        return cls(**field_validation)
