
from .. import FieldValidationInfo, ValidationStatus, ObjectValidationInfo
from ..common.validator import CommonFieldValidator


class IndicatorValidationInfo(ObjectValidationInfo):

    def __init__(self, **field_validation):
        super(IndicatorValidationInfo, self).__init__(**field_validation)

    @staticmethod
    def validate(**indicator_data):
        common_field_validation = CommonFieldValidator.validate(**indicator_data)

        indicator_types_validation = None

        if not indicator_data.get('indicator_types'):
            indicator_types_validation = FieldValidationInfo(ValidationStatus.ERROR, 'No indicator types.')

        return IndicatorValidationInfo(indicator_types=indicator_types_validation, **common_field_validation)
