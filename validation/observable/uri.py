
from .. import ValidationStatus, FieldValidationInfo
from .observable import ObservableValidationInfo
import re
from urlparse import urlparse


class URIValidationInfo(ObservableValidationInfo):

    TYPE = 'URIObjectType'

    URN_MATCHER = re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$", re.IGNORECASE)

    URN_TYPE = 'URN'
    URL_TYPE = 'URL'

    def __init__(self, **field_validation):
        super(URIValidationInfo, self).__init__(URIValidationInfo.TYPE, **field_validation)

    @classmethod
    def validate(cls, **observable_data):
        type_validation = None
        value_validation = None

        uri_type = observable_data.get('type')
        uri_value = observable_data.get('value')

        if uri_type == cls.URN_TYPE and not cls.URN_MATCHER.match(uri_value):
            value_validation = FieldValidationInfo(ValidationStatus.WARN, 'URN value may be invalid')
        elif uri_type == cls.URL_TYPE:
            url_parse_result = urlparse(uri_value)
            if not url_parse_result.scheme or not url_parse_result.netloc:
                value_validation = FieldValidationInfo(ValidationStatus.WARN, 'URL value may be invalid')
        elif uri_type:
            type_validation = FieldValidationInfo(ValidationStatus.ERROR,
                                                  'Unable to determine URI type (%s)' % uri_type)
        else:
            type_validation = FieldValidationInfo(ValidationStatus.ERROR, 'URI type is missing')

        if not uri_value:
            value_validation = FieldValidationInfo(ValidationStatus.ERROR, 'URI value is missing')

        return cls(value=value_validation, type=type_validation)
