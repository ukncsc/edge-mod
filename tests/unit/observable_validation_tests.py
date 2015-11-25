import unittest
from adapters.certuk_mod.validation.observable.observable import ObservableValidationInfo
from adapters.certuk_mod.validation import ValidationStatus


class ObservableValidationInfoTests(unittest.TestCase):

    def test_Constructor_IfNoType_Error(self):
        validation_info = ObservableValidationInfo(None, {'description': 'blah'})
        self.assertEqual(validation_info.object_type.status, ValidationStatus.ERROR)

    def test_Constructor_IfInvalidType_Error(self):
        validation_info = ObservableValidationInfo(ObservableValidationInfo.TYPE, {'description': 'blah'})
        self.assertEqual(validation_info.object_type.status, ValidationStatus.WARN)

    def test_Constructor_IfNoDescription_Info(self):
        validation_info = ObservableValidationInfo('SomeType', {})
        self.assertEqual(validation_info.description.status, ValidationStatus.INFO)

    def test_Validate_IfCalled_RaiseNotImplemented(self):
        self.assertRaises(NotImplementedError, ObservableValidationInfo.validate)
