
class ValidationStatus(object):
    OK = "OK"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class FieldValidationInfo(object):

    def __init__(self, status, message, field_path_name=None):
        super(FieldValidationInfo, self).__init__()
        self.status = status
        self.message = message
        self.field_path_name = field_path_name


class FieldAlias(object):

    def __init__(self, field_path_name, field_value):
        super(FieldAlias, self).__init__()
        self.field_path_name = field_path_name
        self.field_value = field_value


class ObjectValidationInfo(object):

    def __init__(self, **field_validation):
        super(ObjectValidationInfo, self).__init__()
        self.validation_dict = {}
        for field_name, field_results in field_validation.iteritems():
            if field_results and field_results.status != ValidationStatus.OK:
                actual_field_name = field_results.field_path_name if field_results.field_path_name else field_name
                self.validation_dict[actual_field_name] = {
                    'status': field_results.status,
                    'message': field_results.message
                }
