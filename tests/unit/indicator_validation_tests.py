import unittest
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.indicator.indicator import IndicatorValidationInfo


class IndicatorValidationInfoTests(unittest.TestCase):

    def test_Validate_MissingFields_Error(self):
        validation_info = IndicatorValidationInfo.validate()
        self.assertEqual(validation_info.title.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.description.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.tlp.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.indicator_types.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.phase_id.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.confidence.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.indicated_ttps.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.suggested_coas.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.observables.status, ValidationStatus.ERROR)

    def test_Validate_InvalidFields_Error(self):
        validation_info = IndicatorValidationInfo.validate(
            confidence='test',
            phase_id='test'
        )
        self.assertEqual(validation_info.confidence.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.phase_id.status, ValidationStatus.ERROR)

    def test_Validate_ConfidenceUnknown_Warn(self):
        validation_info = IndicatorValidationInfo.validate(
            confidence='Unknown',
        )
        self.assertEqual(validation_info.confidence.status, ValidationStatus.WARN)

    def test_Validate_NoShortDescription_Info(self):
        validation_info = IndicatorValidationInfo.validate()
        self.assertEqual(validation_info.short_description.status, ValidationStatus.INFO)

    def test_Validate_AllFieldsValid_Pass(self):
        validation_info = IndicatorValidationInfo.validate(
            title='test',
            description='description...',
            short_description='hi',
            tlp='RED',
            phase_id='stix:TTP-af1016d6-a744-4ed7-ac91-00fe2272185a',
            indicator_types='IP Watchlist',
            confidence='High',
            indicated_ttps=['test'],
            suggested_coas=['test'],
            observable=['test']
        )
        self.assertIsNone(validation_info.title)
        self.assertIsNone(validation_info.description)
        self.assertIsNone(validation_info.short_description)
        self.assertIsNone(validation_info.tlp)
        self.assertIsNone(validation_info.indicator_types)
        self.assertIsNone(validation_info.phase_id)
        self.assertIsNone(validation_info.confidence)
        self.assertIsNone(validation_info.indicated_ttps)
        self.assertIsNone(validation_info.suggested_coas)
        self.assertIsNone(validation_info.observables)
