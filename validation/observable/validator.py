
from observable import ObservableValidationInfo
from address import AddressValidationInfo


class ObservableValidator(object):

    UNKNOWN_TYPE_HANDLER = ObservableValidationInfo.validate

    @staticmethod
    def validate(**observable_data):
        handler = ObservableValidator.__get_validation_handler(observable_data['object_type'])
        return handler(**observable_data)

    @staticmethod
    def __get_validation_handler(object_type):
        handler_map = {
            'AddressObjectType': AddressValidationInfo.validate
        }
        handler = handler_map.get(object_type)
        if handler is None:
            handler = ObservableValidator.UNKNOWN_TYPE_HANDLER
        return handler
