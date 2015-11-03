
from .. import ValidationStatus, FieldValidationInfo
from .observable import ObservableValidationInfo


class MutexValidationInfo(ObservableValidationInfo):

    TYPE = 'MutexObjectType'

    def __init__(self, **field_validation):
        super(MutexValidationInfo, self).__init__(MutexValidationInfo.TYPE, **field_validation)
        self.name = field_validation.get('name')

    @classmethod
    def validate(cls, **observable_data):
        name = observable_data.get('name')
        if name:
            name_validation = None
        else:
            name_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Mutex name is missing')

        return cls(name=name_validation)
