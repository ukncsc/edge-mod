
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from observable import ObservableValidationInfo
from domain import DomainNameValidationInfo
import re


class HostnameValidationInfo(ObservableValidationInfo):

    TYPE = 'HostnameObjectType'

    HOSTNAME_MATCHER = re.compile(
        r'^[A-Z]+(?:(?:[A-Z0-9]|[A-Z0-9][A-Z0-9\-]*[A-Z0-9])\.)*(?:[A-Z0-9]|[A-Z0-9][A-Z0-9\-]*[A-Z0-9])$',
        re.IGNORECASE)

    def __init__(self, observable_data, **field_validation):
        super(HostnameValidationInfo, self).__init__(HostnameValidationInfo.TYPE, observable_data, **field_validation)
        self.hostname_value = field_validation.get('hostname_value')

    @classmethod
    def validate(cls, **observable_data):
        value = observable_data.get('hostname_value')
        if value:
            value_validation = cls.validate_hostname_value(observable_data.get('is_domain_name', False), value)
        else:
            value_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Hostname value is missing')
        return cls(observable_data, hostname_value=value_validation)

    @staticmethod
    def validate_hostname_value(is_domain, value):
        if is_domain:
            is_valid = DomainNameValidationInfo.get_domain_type_from_value(value) is not None
        else:
            is_valid = HostnameValidationInfo.HOSTNAME_MATCHER.match(value) is not None

        error = 'Invalid %s value' % ('domain' if is_domain else 'hostname')

        return None if is_valid else FieldValidationInfo(ValidationStatus.WARN, error)
