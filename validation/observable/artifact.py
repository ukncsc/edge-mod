
from .. import ValidationStatus, FieldValidationInfo
from .observable import ObservableValidationInfo


class ArtifactValidationInfo(ObservableValidationInfo):

    TYPE = 'ArtifactObjectType'

    def __init__(self, **field_validation):
        super(ArtifactValidationInfo, self).__init__(ArtifactValidationInfo.TYPE, **field_validation)

    @classmethod
    def validate(cls, **observable_data):
        type_validation = None
        raw_artifact_validation = None

        if not observable_data.get('type'):
            type_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Artifact type is missing')

        if not observable_data.get('raw_artifact'):
            raw_artifact_validation = FieldValidationInfo(ValidationStatus.ERROR, 'Artifact data is missing')

        return cls(type=type_validation, raw_artifact=raw_artifact_validation,
                   description=observable_data.get('description'))
