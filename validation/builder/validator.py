
from adapters.certuk_mod.validation.common.structure import IndicatorStructureConverter
from adapters.certuk_mod.validation.indicator.validator import IndicatorValidator


class BuilderValidationInfo(object):

    def __init__(self, builder_dict):
        super(BuilderValidationInfo, self).__init__()
        self.builder_dict = builder_dict
        self.validation_dict = self.__generate_validation_dict(builder_dict)

    @staticmethod
    def __generate_validation_dict(builder_dict):
        validation_dict = {}
        validation_dict.update(BuilderValidationInfo.__validate_indicator(builder_dict))
        validation_dict.update(BuilderValidationInfo.__validate_observables(builder_dict))

        return validation_dict

    @staticmethod
    def __validate_indicator(builder_dict):
        indicator = IndicatorStructureConverter.builder_to_simple(builder_dict)
        validation_result = IndicatorValidator.validate(**indicator)
        return {
            indicator['id']: validation_result.validation_dict
        }

    @staticmethod
    def __validate_observables(builder_dict):
        # Need to map between structure defined in ind-build-obs*->save() method,
        #   and structure defined in the ObservableValidationInfo classes...
        # So, will need an ObservableStructureConverter.builder_to_simple method.
        observables = {}
        return {}
