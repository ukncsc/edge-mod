import unittest
import mock
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.email_type import EmailValidationInfo


class EmailValidationTests(unittest.TestCase):

    VALID_PROPERTIES = [
        ('from', 'dummy address', 'from_address'),
        ('date', '2015-11-16T13:00:00Z', 'date'),
        ('subject', 'blah', 'subject')
    ]

    def test_Validate_IfNoSubjectAndFromAndDate_Error(self):
        email_validation = EmailValidationInfo.validate()
        self.assertEqual(email_validation.subject.status if email_validation.subject else None, ValidationStatus.ERROR)
        self.assertEqual(email_validation.from_address.status if email_validation.from_address else None,
                         ValidationStatus.ERROR)
        self.assertEqual(email_validation.date.status if email_validation.date else None, ValidationStatus.ERROR)
        self.assertIsNone(email_validation.to)
        self.assertIsNone(email_validation.cc)
        self.assertIsNone(email_validation.bcc)

    @mock.patch('adapters.certuk_mod.validation.observable.address.AddressValidationInfo.EMAIL_MATCHER')
    def test_Validate_IfInvalidFrom_Warn(self, mock_email_matcher):
        mock_email_matcher.match.return_value = None
        properties = {
            'from': 'Dummy address'
        }
        email_validation = EmailValidationInfo.validate(**properties)
        self.assertEqual(email_validation.from_address.status if email_validation.from_address else None,
                         ValidationStatus.WARN)

    def test_Validate_IfInvalidDate_Warn(self):
        email_validation = EmailValidationInfo.validate(date='22-13-2015')
        self.assertEqual(email_validation.date.status if email_validation.date else None, ValidationStatus.WARN)

    @mock.patch('adapters.certuk_mod.validation.observable.address.AddressValidationInfo.EMAIL_MATCHER')
    def test_Validate_IfInvalidToCcBcc_Warn(self, mock_email_matcher):
        mock_email_matcher.match.return_value = None
        email_validation = EmailValidationInfo.validate(to=['dummy@address'], cc=['dummy@address'],
                                                        bcc=['dummy@address'])

        self.assertEqual(email_validation.to.status, ValidationStatus.WARN)
        self.assertEqual(email_validation.cc.status, ValidationStatus.WARN)
        self.assertEqual(email_validation.bcc.status, ValidationStatus.WARN)

    def test_Validate_IfNoToCcBcc_NoWarn(self):
        email_validation = EmailValidationInfo.validate(subject='Test')

        self.assertIsNone(email_validation.to)
        self.assertIsNone(email_validation.cc)
        self.assertIsNone(email_validation.bcc)

    @mock.patch('adapters.certuk_mod.validation.observable.address.AddressValidationInfo.EMAIL_MATCHER')
    def test_Validate_AtLeastOneOfSubjectOrFromOrDate_Pass(self, mock_email_matcher):
        mock_email_matcher.match.return_value = True
        for property_info in self.VALID_PROPERTIES:
            properties = {
                property_info[0]: property_info[1]
            }
            email_validation = EmailValidationInfo.validate(**properties)
            self.assertIsNone(getattr(email_validation, property_info[2], None))
