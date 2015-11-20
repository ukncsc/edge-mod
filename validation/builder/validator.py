
from adapters.certuk_mod.validation.common.structure import IndicatorStructureConverter, ObservableStructureConverter, OtherStructureConverter
from adapters.certuk_mod.validation.common.namespace import NamespaceValidationInfo
from adapters.certuk_mod.validation.indicator.validator import IndicatorValidator
from adapters.certuk_mod.validation.observable.validator import ObservableValidator
from adapters.certuk_mod.validation import ValidationStatus


class BuilderValidationInfo(object):

    def __init__(self, builder_dict):
        super(BuilderValidationInfo, self).__init__()
        self.builder_dict = builder_dict
        self.validation_dict = self.__generate_validation_dict(builder_dict)

    @classmethod
    def validate(cls, builder_dict):
        return cls(builder_dict)

    @staticmethod
    def __generate_validation_dict(builder_dict):
        validation_dict = {}
        validation_dict.update(BuilderValidationInfo.__validate_indicator(
            IndicatorStructureConverter.builder_to_simple(builder_dict)
        ))
        validation_dict.update(BuilderValidationInfo.__validate_observables(
            builder_dict.get('observables', {})
        ))

        return validation_dict

    @staticmethod
    def __validate_indicator(indicator):
        validation_result = IndicatorValidator.validate(**indicator)

        # Bit of a fudge here, but we have different rules for internal/external publish for confidence value...
        confidence_validation = validation_result.confidence
        if confidence_validation and confidence_validation.status == ValidationStatus.ERROR:
            confidence_validation.status = ValidationStatus.WARN

        return {
            indicator['id']: validation_result.validation_dict
        }

    @staticmethod
    def __validate_observables(observables):
        # Need to map between structure defined in ind-build-obs*->save() method,
        #   and structure defined in the ObservableValidationInfo classes...
        # So, will need an ObservableStructureConverter.builder_to_simple method.
        validation_results = {}
        dummy_id = 1
        for observable in observables:
            id_ = observable.get('id')
            object_type = observable.get('objectType')
            if not id_:
                # No id, so we can safely assume this is something from the builder...
                observable_properties = ObservableStructureConverter.builder_to_simple(object_type, observable)
                validation_info = ObservableValidator.validate(**observable_properties)
                validation_results['Observable ' + str(dummy_id)] = validation_info.validation_dict
            else:
                # Observables with an ID may or may not be something created by us, so we will need to do the
                #   NamespaceValidationInfo check thingy...
                namespace_validation = NamespaceValidationInfo.validate(r'obs', id_)
                if namespace_validation.is_local():
                    # I guess we need to retrieve the object from the database, using the id.
                    # Then we need to convert the object (probably an EdgeObject) to something our validators understand.
                    # Probably easiest to call EdgeObject.capsulize (to convert to package), then call package_to_simple...
                    pass
                else:
                    validation_results.update({id_: namespace_validation.validation_dict})
            dummy_id += 1
        return validation_results
