
from .. import FieldValidationInfo, ValidationStatus


class CommonFieldValidator(object):

    @staticmethod
    def validate(**object_data):
        title_validation = None
        description_validation = None

        if not object_data.get('title'):
            title_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Title missing.')

        if not object_data.get('description'):
            description_validation = FieldValidationInfo(ValidationStatus.INFO, 'Description is missing.')

        return {
            'title': title_validation,
            'description': description_validation
        }
