import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.file import FileValidationInfo


def make_hashes(hash_tuple_array):
    return [{r'type': hash_type, r'simple_hash_value': hash_value} for hash_type, hash_value in hash_tuple_array]


class FileValidationTests(unittest.TestCase):

    def test_Validate_IfNoData_Passes(self):
        file_validation = FileValidationInfo.validate()
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.size_in_bytes)
        self.assertIsNone(file_validation.file_extension)
        self.assertIsNone(file_validation.MD5)
        self.assertIsNone(file_validation.MD6)
        self.assertIsNone(file_validation.SHA1)
        self.assertIsNone(file_validation.SHA224)
        self.assertIsNone(file_validation.SHA256)
        self.assertIsNone(file_validation.SHA384)
        self.assertIsNone(file_validation.SHA512)
        self.assertIsNone(file_validation.SSDEEP)
        self.assertIsNone(file_validation.Other)

    def test_Validate_IfSizeInBytesNonNumeric_Error(self):
        file_validation = FileValidationInfo.validate(size_in_bytes=r'XX')
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.size_in_bytes.status, ValidationStatus.ERROR)

    def test_Validate_IfSizeInBytesNegative_Error(self):
        file_validation = FileValidationInfo.validate(size_in_bytes=-42)
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.size_in_bytes.status, ValidationStatus.ERROR)

    def test_Validate_IfSizeInBytesPositive_Pass(self):
        file_validation = FileValidationInfo.validate(size_in_bytes=42)
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.size_in_bytes)

    def test_Validate_IfFileExtensionInvalid_Warn(self):
        file_validation = FileValidationInfo.validate(file_extension=r'exe')
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.file_extension.status, ValidationStatus.WARN)

    def test_Validate_IfFileExtensionValid_Pass(self):
        file_validation = FileValidationInfo.validate(file_extension=r'.exe')
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.file_extension)

    def test_Validate_IfMD5Invalid_Warn(self):
        file_validation = FileValidationInfo.validate(hashes=make_hashes([(r'MD5', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.MD5.status, ValidationStatus.WARN)

    def test_Validate_IfMD5Valid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'MD5', r'0123456789abcdef0123456789abcdef')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.MD5)

    def test_Validate_IfMD6Invalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'MD6', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.MD6.status, ValidationStatus.WARN)

    def test_Validate_IfMD6Valid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'MD6', r'0123456789abcdef0123456789abcdef01234567')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.MD6)

    def test_Validate_IfSHA1Invalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA1', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.SHA1.status, ValidationStatus.WARN)

    def test_Validate_IfSHA1Valid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA1', r'0123456789abcdef0123456789abcdef01234567')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.SHA1)

    def test_Validate_IfSHA224Invalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA224', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.SHA224.status, ValidationStatus.WARN)

    def test_Validate_IfSHA224Valid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA224', r'0123456789abcdef0123456789abcdef0123456789abcdef01234567')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.SHA224)

    def test_Validate_IfSHA256Invalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA256', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.SHA256.status, ValidationStatus.WARN)

    def test_Validate_IfSHA256Valid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA256', r'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.SHA256)

    def test_Validate_IfSHA384Invalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA384', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.SHA384.status, ValidationStatus.WARN)

    def test_Validate_IfSHA384Valid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA384', r'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.SHA384)

    def test_Validate_IfSHA512Invalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA512', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.SHA512.status, ValidationStatus.WARN)

    def test_Validate_IfSHA512Valid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SHA512', r'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.SHA512)

    def test_Validate_IfSSDeepInvalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SSDEEP', r'invalid')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.SSDEEP.status, ValidationStatus.WARN)

    def test_Validate_IfSSDeepValid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'SSDEEP', r'1234567890:0aZ/+:/+zA0')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.SSDEEP)

    def test_Validate_IfOtherInvalid_Warn(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'Other', r'')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertEqual(file_validation.Other.status, ValidationStatus.WARN)

    def test_Validate_IfOtherValid_Pass(self):
        file_validation = FileValidationInfo.validate(
            hashes=make_hashes([(r'Other', r'0123456789abcdef')]))
        self.assertIsInstance(file_validation, FileValidationInfo)
        self.assertIsNone(file_validation.Other)
