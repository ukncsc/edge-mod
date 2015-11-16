import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.observable.artifact import ArtifactValidationInfo


class ArtifiactValidationTests(unittest.TestCase):

    def test_Validate_IfNoTypeAndData_Error(self):
        artifact_validation = ArtifactValidationInfo.validate()
        self.assertEqual(artifact_validation.type.status, ValidationStatus.ERROR)
        self.assertEqual(artifact_validation.raw_artifact.status, ValidationStatus.ERROR)

    def test_Validate_IfTypeAndData_Passes(self):
        artifact_validation = ArtifactValidationInfo.validate(type='Memory Region', raw_artifact='0x1234')
        self.assertIsNone(artifact_validation.type)
        self.assertIsNone(artifact_validation.raw_artifact)
