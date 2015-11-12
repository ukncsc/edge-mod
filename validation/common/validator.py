
from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus


class CommonFieldValidator(object):

    @staticmethod
    def validate(**object_data):
        title_validation = None
        short_description_validation = None
        description_validation = None
        tlp_validation = None

        if not object_data.get('title'):
            title_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Title missing')

        if not object_data.get('short_description'):
            short_description_validation = FieldValidationInfo(ValidationStatus.INFO, 'No short description')

        if not object_data.get('description'):
            description_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Description is missing')

        if not object_data.get('tlp'):
            tlp_validation = FieldValidationInfo(ValidationStatus.ERROR, 'No TLP')

        return {
            'title': title_validation,
            'short_description': short_description_validation,
            'description': description_validation,
            'tlp': tlp_validation
        }
