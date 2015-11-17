
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from observable import ObservableValidationInfo
import re


class RegistryKeyValidationInfo(ObservableValidationInfo):

    TYPE = 'WindowsRegistryKeyObjectType'

    KEY_MATCHER = re.compile(r'^(?:[^\\]+\\)+[^\\]+$')
    HIVE_MATCHER = re.compile(r'^(?:[^\\]+_)+[^_\\]+(?:\\[^\\]+)*$')

    def __init__(self, **field_validation):
        super(RegistryKeyValidationInfo, self).__init__(RegistryKeyValidationInfo.TYPE, **field_validation)
        self.hive = field_validation.get('hive')
        self.key = field_validation.get('key')

    @classmethod
    def validate(cls, **observable_data):
        hive_validation = None
        key_validation = None

        hive = observable_data.get('hive')
        if hive and not cls.HIVE_MATCHER.match(hive):
            hive_validation = FieldValidationInfo(ValidationStatus.WARN, 'Registry hive may be invalid')

        key = observable_data.get('key')
        if not key:
            key_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Registry key is missing')
        elif not cls.KEY_MATCHER.match(key):
            key_validation = FieldValidationInfo(ValidationStatus.WARN, 'Registry key may be invalid')
        elif hive and key.startswith(hive):
            key_validation = FieldValidationInfo(ValidationStatus.WARN, 'Registry key prepended with hive value')

        return cls(hive=hive_validation, key=key_validation, description=observable_data.get('description'))
