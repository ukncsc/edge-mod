
from .. import FieldValidationInfo, ValidationStatus


class CommonFieldValidator(object):

    @staticmethod
    def validate(**object_data):
        title_validation = None

        if not object_data.get('title'):
            title_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Title missing.')

        return {
            'title': title_validation
        }
