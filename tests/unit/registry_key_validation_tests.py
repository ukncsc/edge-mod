import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.registry_key import RegistryKeyValidationInfo


class RegistryKeyValidationTests(unittest.TestCase):

    def test_Validate_IfNoHive_Pass(self):
        registry_key_validation = RegistryKeyValidationInfo.validate(key=r'a\b')
        self.assertIsInstance(registry_key_validation, RegistryKeyValidationInfo)
        self.assertIsNone(registry_key_validation.hive)
        self.assertIsNone(registry_key_validation.key)

    def test_Validate_IfBadFormatHive_Warn(self):
        registry_key_validation = RegistryKeyValidationInfo.validate(hive=r'\\', key=r'a\b')
        self.assertIsInstance(registry_key_validation, RegistryKeyValidationInfo)
        self.assertEquals(registry_key_validation.hive.status, ValidationStatus.WARN)
        self.assertIsNone(registry_key_validation.key)

    def test_Validate_IfNoKey_Error(self):
        registry_key_validation = RegistryKeyValidationInfo.validate()
        self.assertIsInstance(registry_key_validation, RegistryKeyValidationInfo)
        self.assertIsNone(registry_key_validation.hive)
        self.assertEquals(registry_key_validation.key.status, ValidationStatus.ERROR)

    def test_Validate_IfBadFormatKey_Warn(self):
        registry_key_validation = RegistryKeyValidationInfo.validate(key=r'a')
        self.assertIsInstance(registry_key_validation, RegistryKeyValidationInfo)
        self.assertIsNone(registry_key_validation.hive)
        self.assertEquals(registry_key_validation.key.status, ValidationStatus.WARN)

    def test_Validate_IfKeyPrependedWithHive_Warn(self):
        registry_key_validation = RegistryKeyValidationInfo.validate(hive=r'a_b', key=r'a_b\c')
        self.assertIsInstance(registry_key_validation, RegistryKeyValidationInfo)
        self.assertIsNone(registry_key_validation.hive)
        self.assertEquals(registry_key_validation.key.status, ValidationStatus.WARN)
