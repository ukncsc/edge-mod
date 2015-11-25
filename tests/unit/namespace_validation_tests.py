import unittest
import mock
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.common.namespace import NamespaceValidationInfo


@mock.patch('adapters.certuk_mod.validation.common.namespace.LOCAL_ALIAS', 'BLAH')
class NamespaceValidationTests(unittest.TestCase):

    def test_Validate_IfLocal_Pass(self):
        namespace_validation_info = NamespaceValidationInfo.validate(None, 'BLAH:1234')
        self.assertIsInstance(namespace_validation_info, NamespaceValidationInfo)
        self.assertIsNone(namespace_validation_info.namespace)

    def test_Validate_IfNotLocal_Warn(self):
        namespace_validation_info = NamespaceValidationInfo.validate(None, 'NOT-BLAH:1234')
        self.assertIsInstance(namespace_validation_info, NamespaceValidationInfo)
        self.assertEqual(namespace_validation_info.namespace.status, ValidationStatus.WARN)

    def test_IsLocal_IfLocal_ReturnTrue(self):
        namespace_validation_info = NamespaceValidationInfo.validate(None, 'BLAH:1234')
        self.assertTrue(namespace_validation_info.is_local())

    def test_IsLocal_IfNotLocal_ReturnFalse(self):
        namespace_validation_info = NamespaceValidationInfo.validate(None, 'NOT-BLAH:1234')
        self.assertFalse(namespace_validation_info.is_local())
