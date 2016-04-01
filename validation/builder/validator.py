from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.common.namespace import NamespaceValidationInfo
from adapters.certuk_mod.validation.common.structure import (
    IndicatorStructureConverter,
    ObservableStructureConverter
)
from adapters.certuk_mod.validation.indicator.indicator import IndicatorValidationInfo
from adapters.certuk_mod.validation.incident.incident import IncidentValidationInfo
from adapters.certuk_mod.validation.observable.validator import ObservableValidator
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from edge.generic import EdgeObject, EdgeError


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
        if builder_dict['stixtype'] == "ind":
            validation_dict.update(BuilderValidationInfo.__validate_indicator(
                IndicatorStructureConverter.builder_to_simple(builder_dict)
            ))
            validation_dict.update(BuilderValidationInfo.__validate_observables(
                builder_dict.get('observables', {})
            ))
        elif builder_dict['stixtype'] == "inc":
            validation_dict.update(BuilderValidationInfo.__validate_incident(
                builder_dict
            ))

        return validation_dict

    @staticmethod
    def __validate_indicator(indicator):
        validation_result = IndicatorValidationInfo.validate(**indicator)

        return {
            indicator['id']: validation_result.validation_dict
        }

    @staticmethod
    def __validate_incident(incident):
        validation_result = IncidentValidationInfo.validate(**incident)

        return {
            incident['id']: validation_result.validation_dict
        }

    @staticmethod
    def __validate_observables(observables):
        def can_load(id_):
            try:
                EdgeObject.load(id_)
                return True
            except EdgeError as e:
                return False


        validation_results = {}
        dummy_id = 1
        for observable in observables:
            id_ = observable.get('id')
            object_type = observable.get('objectType')
            if not id_ or not can_load(id_):
                # No id or perhaps a draft id, so we can safely assume this is something from the builder...
                observable_properties = ObservableStructureConverter.builder_to_simple(object_type, observable)
                validation_info = ObservableValidator.validate(**observable_properties)
                validation_results['Observable ' + str(dummy_id)] = validation_info.validation_dict
            else:
                namespace_validation = NamespaceValidationInfo.validate(r'obs', id_)
                if namespace_validation.is_local():
                    real_observable = EdgeObject.load(id_)
                    as_package, _ = real_observable.capsulize('temp')
                    validation_info = PackageValidationInfo.validate(as_package)
                    validation_results.update(validation_info.validation_dict)
                else:
                    validation_results.update({id_: namespace_validation.validation_dict})
            dummy_id += 1
        return validation_results
