import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.http_session import HTTPSessionValidationInfo


class HTTPSessionValidationTests(unittest.TestCase):

    INVALID_USER_AGENTS = [
        'blah',
        '/'
    ]

    VALID_USER_AGENTS = [
        'Mozilla/5.0',
        'x/y'
        '1/2'
    ]

    def test_Validate_NoUserAgent_Error(self):
        http_session_validation = HTTPSessionValidationInfo.validate()
        self.assertEqual(http_session_validation.user_agent.status, ValidationStatus.ERROR)

    def test_Validate_InvalidUserAgent_Warn(self):
        for user_agent in self.INVALID_USER_AGENTS:
            http_session_validation = HTTPSessionValidationInfo.validate(user_agent=user_agent)
            self.assertEqual(http_session_validation.user_agent.status, ValidationStatus.WARN)

    def test_Validate_ValidUserAgent_Pass(self):
        for user_agent in self.VALID_USER_AGENTS:
            http_session_validation = HTTPSessionValidationInfo.validate(user_agent=user_agent)
            self.assertIsNone(http_session_validation.user_agent)
