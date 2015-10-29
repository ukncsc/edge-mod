
class ValidationStatus(object):
    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"


class FieldValidationInfo(object):

    def __init__(self, status, message):
        super(FieldValidationInfo, self).__init__()
        self.status = status
        self.message = message


class ObjectValidationInfo(object):

    def __init__(self, **field_validation):
        super(ObjectValidationInfo, self).__init__()
        self.validation_dict = {}
        for field_name, field_results in field_validation.iteritems():
            if field_results and field_results.status != ValidationStatus.OK:
                self.validation_dict[field_name] = {
                    'status': field_results.status,
                    'message': field_results.message
                }
