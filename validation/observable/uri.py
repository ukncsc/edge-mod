
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from observable import ObservableValidationInfo
from domain import DomainNameValidationInfo
from cybox.objects.uri_object import URI
import re
from urlparse import urlparse


class URIValidationInfo(ObservableValidationInfo):

    TYPE = 'URIObjectType'

    URN_MATCHER = re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$", re.IGNORECASE)

    SCHEME_MATCHER = re.compile(r'^[a-zA-Z]+$')

    URN_TYPE = URI.TYPE_GENERAL
    URL_TYPE = URI.TYPE_URL
    DOMAIN_TYPE = URI.TYPE_DOMAIN

    def __init__(self, **field_validation):
        super(URIValidationInfo, self).__init__(URIValidationInfo.TYPE, **field_validation)
        self.type = field_validation.get('type')
        self.value = field_validation.get('value')

    @classmethod
    def validate(cls, **observable_data):
        uri_type = observable_data.get('type')
        uri_value = observable_data.get('value')

        type_validation = cls.__validate_type(uri_type)
        value_validation = cls.__validate_value(uri_value, uri_type)

        return cls(value=value_validation, type=type_validation, description=observable_data.get('description'))

    @staticmethod
    def __get_type_map():
        return {
            URIValidationInfo.URN_TYPE: URIValidationInfo.__validate_urn,
            URIValidationInfo.URL_TYPE: URIValidationInfo.__validate_url,
            URIValidationInfo.DOMAIN_TYPE: URIValidationInfo.__validate_domain
        }

    @classmethod
    def __validate_value(cls, value, uri_type):
        if not value:
            return FieldValidationInfo(ValidationStatus.ERROR, 'URI value is missing')

        type_handler = cls.__get_type_map().get(uri_type)
        if type_handler:
            return type_handler(value)

        return None

    @classmethod
    def __validate_type(cls, uri_type):
        if not uri_type:
            return FieldValidationInfo(ValidationStatus.ERROR, 'URI type is missing')

        if uri_type not in cls.__get_type_map():
            return FieldValidationInfo(ValidationStatus.ERROR, 'Unable to determine URI type (%s)' % uri_type)

        return None

    @classmethod
    def __validate_urn(cls, urn):
        if not cls.URN_MATCHER.match(urn):
            return FieldValidationInfo(ValidationStatus.WARN, 'URN value may be invalid')
        return None

    @classmethod
    def __validate_url(cls, url):
        if cls.__is_valid_url(url):
            return None

        return FieldValidationInfo(ValidationStatus.WARN, 'URL value may be invalid')

    @classmethod
    def __is_valid_url(cls, url):
        url_parse_result = urlparse(url)
        return url_parse_result.scheme and cls.SCHEME_MATCHER.match(url_parse_result.scheme) and \
               (url_parse_result.netloc or url_parse_result.path)

    @classmethod
    def __validate_domain(cls, domain):
        if not DomainNameValidationInfo.get_domain_type_from_value(domain):
            return FieldValidationInfo(ValidationStatus.WARN, 'URI domain name value may be invalid')
        return None
