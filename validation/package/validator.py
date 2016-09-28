import json

from adapters.certuk_mod.validation import FieldAlias
from adapters.certuk_mod.validation.common.common import CommonValidationInfo
from adapters.certuk_mod.validation.common.namespace import NamespaceValidationInfo
from adapters.certuk_mod.validation.common.structure import (
    ObservableStructureConverter,
    IndicatorStructureConverter,
    OtherStructureConverter
)
from adapters.certuk_mod.validation.indicator.indicator import IndicatorValidationInfo
from adapters.certuk_mod.validation.observable.validator import ObservableValidator
from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus, ObjectValidationInfo
from edge.combine import STIXPackage
from edge.tools import nested_get


class PackageValidationInfo(object):
    def __init__(self, package_dict):
        self.package_dict = package_dict
        self.validation_dict = PackageValidationInfo.__generate_validation_dict(package_dict)

    @staticmethod
    def __generate_validation_dict(package_dict):
        stix_header = package_dict.get(r'stix_header')
        validation = {}
        validation.update(PackageValidationInfo.__validate_observables(
            nested_get(package_dict, [r'observables', r'observables']), stix_header
        ))
        validation.update(PackageValidationInfo.__validate_indicators(
            nested_get(package_dict, [r'indicators']), stix_header
        ))
        validation.update(PackageValidationInfo.__validate_incidents(
            nested_get(package_dict, [r'incidents']), stix_header
        ))
        # and other types - namespace and TLP checks only ...
        validation.update(PackageValidationInfo.__validate_other(
            nested_get(package_dict, [r'courses_of_action']), r'coa', stix_header
        ))
        validation.update(PackageValidationInfo.__validate_other(
            nested_get(package_dict, [r'ttps', r'ttps']), r'ttp', stix_header
        ))

        return validation

    @staticmethod
    def __validate_observables(observables, stix_header):
        observable_validation = {}
        for observable in observables:
            if 'observable_composition' not in observable:
                id_ = observable['id']
                namespace_validation = NamespaceValidationInfo.validate(r'obs', id_)
                if namespace_validation.is_local():
                    properties = observable['object']['properties']
                    properties = ObservableStructureConverter.package_to_simple(properties.get('xsi:type'), properties)
                    validation_results = ObservableValidator.validate(
                        object_type=FieldAlias('xsi:type', properties.get('xsi:type')),
                        description=observable.get('description'), **properties)
                    validation_results.extend(CommonValidationInfo.validate(item = observable, package_dict = stix_header))
                    if validation_results and validation_results.validation_dict:
                        observable_validation.update({id_: validation_results.validation_dict})
                else:
                    observable_validation.update({id_: namespace_validation.validation_dict})
        return observable_validation

    @staticmethod
    def __validate_incidents(incidents, stix_header):
        incident_validation = {}

        for incident in incidents:
            id_ = incident['id']
            namespace_validation = NamespaceValidationInfo.validate(r'inc', id_)
            if namespace_validation.is_local():
                other_properties = OtherStructureConverter.package_to_simple(incident, stix_header)
                validation_results = CommonValidationInfo.validate(item=incident, package_dict=stix_header)
                if len(other_properties.get('external_ids', [])):
                    validation_results.extend({'external_ids': FieldValidationInfo(ValidationStatus.WARN, r'External IDs exist within an Incident in the package')})
                if validation_results and validation_results.validation_dict:
                    incident_validation.update({id_: validation_results.validation_dict})
            else:
                incident_validation.update({id_: namespace_validation.validation_dict})

        return incident_validation

    @staticmethod
    def __validate_indicators(indicators, stix_header):
        indicator_validation = {}
        for indicator in indicators:
            id_ = indicator['id']
            namespace_validation = NamespaceValidationInfo.validate(r'ind', id_)
            if namespace_validation.is_local():
                indicator_properties = IndicatorStructureConverter.package_to_simple(indicator, stix_header)
                validation_results = IndicatorValidationInfo.validate(**indicator_properties)
                validation_results.extend(CommonValidationInfo.validate(item=indicator, package_dict=stix_header))
                if validation_results and validation_results.validation_dict:
                    indicator_validation.update({id_: validation_results.validation_dict})
            else:
                indicator_validation.update({id_: namespace_validation.validation_dict})
        return indicator_validation

    @staticmethod
    def __validate_other(other_objects, type_, stix_header):
        other_validation = {}
        for other_object in other_objects:
            id_ = other_object['id']
            namespace_validation = NamespaceValidationInfo.validate(type_, id_)
            if namespace_validation.is_local():
                validation_results = CommonValidationInfo.validate(item=other_object, package_dict = stix_header)
                if validation_results and validation_results.validation_dict:
                    other_validation.update({id_: validation_results.validation_dict})
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
