import unittest
from adapters.certuk_mod.tests import unit
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.incident.incident import IncidentValidationInfo


class IncidentValidationInfoTests(unittest.TestCase):

    def test_Validate_MissingFields_Error(self):
        validation_info = IncidentValidationInfo.validate()
        self.assertEqual(validation_info.title.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.description.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.tlp.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.status.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.confidence.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.reporter.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.categories.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.trustgroups.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.effects.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.victims.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.responders.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.discovery_methods.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.intended_effects.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.related_indicators, None)
        self.assertEqual(validation_info.related_observables, None)
        self.assertEqual(validation_info.leveraged_ttps.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.attributed_actors, None)
        self.assertEqual(validation_info.related_incidents, None)
        self.assertEqual(validation_info.coordinators.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.coordinators.time, ValidationStatus.ERROR)

    def test_Validate_InvalidFields_Error(self):
        validation_info = IncidentValidationInfo.validate(
                confidence='test',
                status='test'
        )
        self.assertEqual(validation_info.confidence.status, ValidationStatus.ERROR)
        self.assertEqual(validation_info.status.status, ValidationStatus.ERROR)

    def test_Validate_ConfidenceUnknown_Warn(self):
        validation_info = IncidentValidationInfo.validate(
                confidence='Unknown',
        )
        self.assertEqual(validation_info.confidence.status, ValidationStatus.WARN)

    def test_Validate_NoShortDescription_Info(self):
        validation_info = IncidentValidationInfo.validate()
        self.assertEqual(validation_info.short_description.status, ValidationStatus.INFO)

    def test_Validate_AllFieldsValid_Pass(self):
        validation_info = IncidentValidationInfo.validate(
                title='test',
                description='description...',
                short_description='hi',
                tlp='RED',
                status='Stalled',
                reporter="Bob",
                confidence='High',
                categories=['test'],
                trustgroups=['test'],
                effects=['test'],
                victims=['test'],
                responders=['test'],
                discovery_methods=['test'],
                intended_effects=['test'],
                related_indicators=['test'],
                related_observables=['test'],
                leveraged_ttps=['test'],
                attributed_actors=['test'],
                related_incidents=['test'],
                coordinators=['test'],
                time={'incident_opened':{"value":"test"}}
        )
        self.assertIsNone(validation_info.title)
        self.assertIsNone(validation_info.description)
        self.assertIsNone(validation_info.short_description)
        self.assertIsNone(validation_info.tlp)
        self.assertIsNone(validation_info.status)
        self.assertIsNone(validation_info.reporter)
        self.assertIsNone(validation_info.categories)
        self.assertIsNone(validation_info.trustgroups)
        self.assertIsNone(validation_info.effects)
        self.assertIsNone(validation_info.victims)

        self.assertIsNone(validation_info.responders)
        self.assertIsNone(validation_info.discovery_methods)
        self.assertIsNone(validation_info.intended_effects)
        self.assertIsNone(validation_info.related_indicators)
        self.assertIsNone(validation_info.related_observables)
        self.assertIsNone(validation_info.leveraged_ttps)
        self.assertIsNone(validation_info.attributed_actors)
        self.assertIsNone(validation_info.related_incidents)
        self.assertIsNone(validation_info.coordinators)
        self.assertIsNone(validation_info.time)
