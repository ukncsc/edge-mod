
from observable import ObservableValidationInfo
from address import AddressValidationInfo
from hostname import HostnameValidationInfo
from domain import DomainNameValidationInfo
from .. import FieldAlias


class ObservableValidator(object):

    @staticmethod
    def validate(**observable_data):
        handler = ObservableValidator.__get_validation_handler(observable_data['object_type'])
        return handler(**observable_data)

    @staticmethod
    def __get_validation_handler(object_type):
        handler_map = {
            AddressValidationInfo.TYPE: AddressValidationInfo.validate,
            HostnameValidationInfo.TYPE: HostnameValidationInfo.validate,
            DomainNameValidationInfo.TYPE: DomainNameValidationInfo.validate
        }
        actual_type = object_type.field_value if isinstance(object_type, FieldAlias) else object_type
        handler = handler_map.get(actual_type)
        if handler is None:
            handler = ObservableValidator.__unknown_type_handler
        return handler

    @staticmethod
    def __unknown_type_handler(**observable_data):
        return ObservableValidationInfo(observable_type=observable_data['object_type'],
                                        description=observable_data.get('description'),
                                        unknown_type=True)
