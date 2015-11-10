
from .. import ValidationStatus, FieldValidationInfo
from .observable import ObservableValidationInfo
from .address import AddressValidationInfo
from dateutil.parser import parse as parse_date


class EmailValidationInfo(ObservableValidationInfo):

    TYPE = 'EmailMessageObjectType'

    def __init__(self, **field_validation):
        super(EmailValidationInfo, self).__init__(EmailValidationInfo.TYPE, **field_validation)
        self.subject = field_validation.get('subject')
        self.from_address = field_validation.get('from_address')
        self.date = field_validation.get('date')
        self.to = field_validation.get('to')
        self.cc = field_validation.get('cc')
        self.bcc = field_validation.get('bcc')

    @classmethod
    def validate(cls, **observable_data):
        subject_validation = None
        from_validation = None
        date_validation = None
        to_validation = None
        cc_validation = None
        bcc_validation = None

        if not (observable_data.get('subject') or observable_data.get('from') or observable_data.get('date')):
            subject_validation = from_validation = date_validation = \
                FieldValidationInfo(ValidationStatus.ERROR,
                                    'Email requires at least one of Subject, From or Date fields')
        else:
            if not cls.__validate_address(observable_data.get('from')):
                from_validation = FieldValidationInfo(ValidationStatus.WARN, 'Email From address may be invalid')
            if not cls.__validate_date(observable_data.get('date')):
                date_validation = FieldValidationInfo(ValidationStatus.WARN, 'Email Date may be invalid')
            to_validation = cls.__validate_address_list(observable_data.get('to'), 'To')
            cc_validation = cls.__validate_address_list(observable_data.get('cc'), 'Cc')
            bcc_validation = cls.__validate_address_list(observable_data.get('bcc'), 'Bcc')

        return cls(description=observable_data.get('description'), subject=subject_validation,
                   from_address=from_validation, date=date_validation, to=to_validation, cc=cc_validation,
                   bcc=bcc_validation)

    @staticmethod
    def __validate_address_list(address_list, address_field_name):
        if address_list:
            for address in address_list:
                if not EmailValidationInfo.__validate_address(address):
                    return FieldValidationInfo(ValidationStatus.WARN,
                                               'An email address in the %s field may be invalid' % address_field_name)
        return None

    @staticmethod
    def __validate_address(address):
        if address and not AddressValidationInfo.EMAIL_MATCHER.match(address):
            return False
        # empty address is ok...
        return True

    @staticmethod
    def __validate_date(date):
        if date:
            try:
                parse_date(date)
            except ValueError:
                return False
        # empty date is ok...
        return True
