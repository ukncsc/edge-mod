from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus, ObjectValidationInfo
from adapters.certuk_mod.validation.common.validator import CommonFieldValidator
from stix.common.vocabs import HighMediumLow


class IndicatorValidationInfo(ObjectValidationInfo):

    CONFIDENCE_VALUES = (
        HighMediumLow.TERM_NONE,
        HighMediumLow.TERM_LOW,
        HighMediumLow.TERM_MEDIUM,
        HighMediumLow.TERM_HIGH,
        HighMediumLow.TERM_UNKNOWN
    )

    def __init__(self, **field_validation):
        super(IndicatorValidationInfo, self).__init__(**field_validation)
        self.indicator_types = field_validation.get('indicator_types')
        self.phase_id = field_validation.get('phase_id')
        self.confidence = field_validation.get('confidence')
        self.indicated_ttps = field_validation.get('indicated_ttps')
        self.suggested_coas = field_validation.get('suggested_coas')
        self.observables = field_validation.get('observables')

    @staticmethod
    def __validate_kill_chain_phase_id(phase_id):
        return bool([k for k in KILL_CHAIN_PHASES if k['phase_id'] == phase_id])

    @classmethod
    def validate(cls, **indicator_data):
        common_field_validation = CommonFieldValidator.validate(**indicator_data)

        if not indicator_data.get('indicator_types'):
            common_field_validation['indicator_types'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                             'No Indicator types')

        kill_chain_phase = indicator_data.get('phase_id')
        if not kill_chain_phase:
            common_field_validation['phase_id'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Kill Chain Phase')
        elif not IndicatorValidationInfo.__validate_kill_chain_phase_id(kill_chain_phase):
            common_field_validation['phase_id'] = FieldValidationInfo(
                ValidationStatus.ERROR, 'The supplied Kill Chain Phase is not recognized internally')

        confidence = indicator_data.get('confidence')
        if confidence not in cls.CONFIDENCE_VALUES:
            common_field_validation['confidence'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                        'No valid Indicator confidence value')
        elif confidence == HighMediumLow.TERM_UNKNOWN:
            common_field_validation['confidence'] = FieldValidationInfo(
                ValidationStatus.WARN, 'Indicator confidence value is set to \'Unknown\'')

        if not indicator_data.get('indicated_ttps'):
            common_field_validation['indicated_ttps'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Indicated TTPs')

        if not indicator_data.get('suggested_coas'):
            common_field_validation['suggested_coas'] = FieldValidationInfo(ValidationStatus.ERROR, 'No Suggested COAs')

        if not indicator_data.get('observable'):
            common_field_validation['observables'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                         'No Indicator Observables')

        return cls(**common_field_validation)
