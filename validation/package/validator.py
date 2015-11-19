
from edge.combine import STIXPackage
from edge.tools import nested_get
import json
from structure import ObservableStructureConverter, IndicatorStructureConverter
from adapters.certuk_mod.validation.common.namespace import NamespaceValidationInfo
from adapters.certuk_mod.validation.observable.validator import ObservableValidator
from adapters.certuk_mod.validation.indicator.validator import IndicatorValidator
from adapters.certuk_mod.validation import FieldAlias


class PackageValidationInfo(object):

    def __init__(self, package_dict):
        self.package_dict = package_dict
        self.validation_dict = PackageValidationInfo.__generate_validation_dict(package_dict)

    @staticmethod
    def __generate_validation_dict(package_dict):
        validation = {}
        validation.update(PackageValidationInfo.__validate_observables(package_dict))
        validation.update(PackageValidationInfo.__validate_indicators(package_dict))
        # and other types - namespace only checks...
        validation.update(PackageValidationInfo.__validate_other(package_dict, r'coa', [r'courses_of_action']))
        validation.update(PackageValidationInfo.__validate_other(package_dict, r'ttp', [r'ttps',r'ttps']))
        validation.update(PackageValidationInfo.__validate_other(package_dict, r'inc', [r'incidents']))
        return validation

    @staticmethod
    def __validate_observables(package_dict):
        observables = nested_get(package_dict, [r'observables', r'observables'])
        observable_validation = {}
        for observable in observables:
            id_ = observable['id']
            namespace_validation = NamespaceValidationInfo.validate(r'obs', id_)
            if namespace_validation.is_local():
                if 'observable_composition' not in observable:
                    properties = observable['object']['properties']
                    properties = ObservableStructureConverter.package_to_simple(properties.get('xsi:type'), properties)
                    validation_results = ObservableValidator.validate(
                        object_type=FieldAlias('xsi:type', properties.get('xsi:type')),
                        description=observable.get('description'), **properties)
                    if validation_results and validation_results.validation_dict:
                        observable_validation.update({id_: validation_results.validation_dict})
            else:
                observable_validation.update({id_: namespace_validation.validation_dict})

        return observable_validation

    @staticmethod
    def __validate_indicators(package_dict):
        indicators = package_dict.get('indicators', {})
        indicator_validation = {}
        for indicator in indicators:
            id_ = indicator['id']
            namespace_validation = NamespaceValidationInfo.validate(r'ind', id_)
            if namespace_validation.is_local():
                indicator_properties = IndicatorStructureConverter.package_to_simple(indicator)
                validation_results = IndicatorValidator.validate(**indicator_properties)
                if validation_results and validation_results.validation_dict:
                    indicator_validation.update({id_: validation_results.validation_dict})
            else:
                indicator_validation.update({id_: namespace_validation.validation_dict})
        return indicator_validation

    @staticmethod
    def __validate_other(package_dict, type_, path):
        other_objects = nested_get(package_dict, path)
        other_validation = {}
        for other_object in other_objects:
            id_ = other_object['id']
            namespace_validation = NamespaceValidationInfo.validate(type_, id_)
            if namespace_validation.is_local():
                pass
            else:
                other_validation.update({id_: namespace_validation.validation_dict})
        return other_validation

    def to_json(self):
        return json.dumps(self.validation_dict)

    @classmethod
    def validate(cls, package):
        if isinstance(package, STIXPackage):
            package_dict = package.to_dict()
        elif isinstance(package, dict):
            package_dict = package
        else:
            raise TypeError('The supplied package must be a valid STIXPackage object or its dict representation.')

        return cls(package_dict)
