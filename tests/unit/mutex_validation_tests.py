import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.mutex import MutexValidationInfo


class MutexValidationTests(unittest.TestCase):

    def test_Validate_IfNoName_Error(self):
        mutex_validation = MutexValidationInfo.validate()
        self.assertEqual(mutex_validation.name.status, ValidationStatus.ERROR)

    def test_Validate_IfName_Pass(self):
        mutex_validation = MutexValidationInfo.validate(name='hf7&%^4')
        self.assertIsNone(mutex_validation.name)
