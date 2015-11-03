
from .. import FieldValidationInfo, ValidationStatus, ObjectValidationInfo
from ..common.validator import CommonFieldValidator
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

    @classmethod
    def validate(cls, **indicator_data):
        common_field_validation = CommonFieldValidator.validate(**indicator_data)

        if not indicator_data.get('indicator_types'):
            common_field_validation['indicator_types'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                             'No Indicator types')

        kill_chain_phases = indicator_data.get('kill_chain_phases')
        if not kill_chain_phases or len(kill_chain_phases) == 0:
            common_field_validation['kill_chain_phases'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                               'No Kill Chain Phase')

        confidence = indicator_data.get('confidence')
        if confidence not in cls.CONFIDENCE_VALUES:
            common_field_validation['confidence'] = FieldValidationInfo(ValidationStatus.ERROR,
                                                                        'No valid Indicator confidence value')
        elif confidence == HighMediumLow.TERM_UNKNOWN:
            common_field_validation['confidence'] = FieldValidationInfo(
                ValidationStatus.WARN, 'Indicator confidence value is set to \'Unknown\'')

        return cls(**common_field_validation)
