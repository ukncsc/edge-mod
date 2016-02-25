from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus, ObjectValidationInfo
from adapters.certuk_mod.validation.common.validator import CommonFieldValidator
from stix.common.vocabs import HighMediumLow
from stix.common.vocabs import IncidentStatus

class IncidentValidationInfo(ObjectValidationInfo):

#ToDo, finish
    CONFIDENCE_VALUES = (
        HighMediumLow.TERM_NONE,
        HighMediumLow.TERM_LOW,
        HighMediumLow.TERM_MEDIUM,
        HighMediumLow.TERM_HIGH,
        HighMediumLow.TERM_UNKNOWN
    )

    STATUS_VALUES = IncidentStatus._ALLOWED_VALUES;

    def __init__(self, **field_validation):
        super(IncidentValidationInfo, self).__init__(**field_validation)
        #Common
        self.title = field_validation.get('title')
        self.tlp = field_validation.get('tlp')
        self.short_description = field_validation.get('short_description')
        self.description = field_validation.get('description')

        #From list or valid values
        self.status = field_validation.get('status')
        self.confidence = field_validation.get('confidence')

        #No check
        self.times = field_validation.get('times')
        self.markers = field_validation.get('markers')

        #At least 1
        self.reporter = field_validation.get('reporter')
        self.categories = field_validation.get('categories')
        self.trustgroups = field_validation.get('trustgroups')
        self.effects = field_validation.get('effects')
        self.victims = field_validation.get('victims')
        self.responders = field_validation.get('responders')
        self.discovery_methods = field_validation.get('discovery_methods')
        self.intended_effects = field_validation.get('intended_effects')
        self.related_indicators = field_validation.get('related_indicators')
        self.related_observables = field_validation.get('related_observables')
        self.leveraged_ttps = field_validation.get('leveraged_ttps')
        self.attributed_actors = field_validation.get('attributed_actors')
        self.related_incidents = field_validation.get('related_incidents')

    @classmethod
    def validate(cls, **incident_data):
        common_field_validation = CommonFieldValidator.validate(**incident_data)

        confidence = incident_data.get('confidence')
        if confidence not in cls.CONFIDENCE_VALUES:
            common_field_validation['confidence'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                        'No valid Indicator confidence value')
        elif confidence == HighMediumLow.TERM_UNKNOWN:
            common_field_validation['confidence'] = FieldValidationInfo(
                ValidationStatus.WARN, 'Indicator confidence value is set to \'Unknown\'')

        status = incident_data.get('status')
        if status not in cls.STATUS_VALUES:
            common_field_validation['status'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                        'No valid Indicator status value')

        if not incident_data.get('reporter'):
            common_field_validation['reporter'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Reporter')
        if not incident_data.get('categories'):
            common_field_validation['categories'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Categories')
        if not incident_data.get('trustgroups'):
            common_field_validation['trustgroups'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Trust Groups')
        if not incident_data.get('effects'):
            common_field_validation['effects'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Effects')
        if not incident_data.get('victims'):
            common_field_validation['victims'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Victims')
        if not incident_data.get('responders'):
            common_field_validation['responders'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Responders')
        if not incident_data.get('discovery_methods'):
            common_field_validation['discovery_methods'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Discovery Methods')
        if not incident_data.get('intended_effects'):
            common_field_validation['intended_effects'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Intended Effects')
        if not incident_data.get('related_observables'):
            common_field_validation['related_observables'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Related Observables')
        if not incident_data.get('related_indicators'):
            common_field_validation['related_indicators'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Related Indicators')
        if not incident_data.get('leveraged_ttps'):
            common_field_validation['leveraged_ttps'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Leveraged TTPs')
        if not incident_data.get('attributed_actors'):
            common_field_validation['attributed_actors'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Attributed Actors')
        if not incident_data.get('related_incidents'):
            common_field_validation['related_incidents'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Related Incidents')

        return cls(**common_field_validation)
