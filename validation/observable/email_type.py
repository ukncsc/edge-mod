
from .. import ValidationStatus, FieldValidationInfo
from .observable import ObservableValidationInfo
from .address import AddressValidationInfo


class EmailValidationInfo(ObservableValidationInfo):

    TYPE = 'EmailObjectType'

    def __init__(self, **field_validation):
        super(EmailValidationInfo, self).__init__(EmailValidationInfo.TYPE, **field_validation)

    @classmethod
    def validate(cls, **observable_data):
        return cls(description=observable_data.get('description'))
