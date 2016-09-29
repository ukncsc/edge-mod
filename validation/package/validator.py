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
        validation.update(PackageValidationInfo.__validate_other(
            nested_get(package_dict, [r'threat_actors']), r'act', stix_header
        ))
        validation.update(PackageValidationInfo.__validate_other(
            nested_get(package_dict, [r'campaigns']), r'cam', stix_header
        ))
        validation.update(PackageValidationInfo.__validate_other(
            nested_get(package_dict, [r'exploit_targets']), r'tgt', stix_header
        ))

        return validation

    @staticmethod
    def __validate_observables(observables, stix_header):
        all_observables_validation = {}
        for observable in observables:
            if 'observable_composition' not in observable:
                id_ = observable['id']
                observable_validation = ObjectValidationInfo()
                observable_validation.extend(CommonValidationInfo.validate(item=observable,
                                                                        package_dict=stix_header))
                namespace_validation = NamespaceValidationInfo.validate(r'obs', id_)
                if namespace_validation.is_local():
                    properties = observable['object']['properties']
                    properties = ObservableStructureConverter.package_to_simple(properties.get('xsi:type'), properties)
                    observable_validation.extend(ObservableValidator.validate(
                        object_type=FieldAlias('xsi:type', properties.get('xsi:type')),
                        description=observable.get('description'), **properties)
                    )
                else:
                    observable_validation.extend(namespace_validation)

                if observable_validation.validation_dict:
                    all_observables_validation.update({id_: observable_validation.validation_dict})

        return all_observables_validation

    @staticmethod
    def __validate_incidents(incidents, stix_header):
        all_incidents_validation = {}

        for incident in incidents:
            id_ = incident['id']
            incident_validation = ObjectValidationInfo()
            incident_validation.extend(CommonValidationInfo.validate(item=incident,
                                                                     package_dict=stix_header))
            namespace_validation = NamespaceValidationInfo.validate(r'inc', id_)
            if namespace_validation.is_local():
                other_properties = OtherStructureConverter.package_to_simple(incident, stix_header)
                if len(other_properties.get('external_ids', [])):
                    field_validation = {'external_ids': {
                        'status': ValidationStatus.WARN,
                        'message': r'External IDs exist within an Incident in the package'}
                    }
                    incident_validation.validation_dict.update(field_validation)
            else:
                incident_validation.extend(namespace_validation)

            if incident_validation.validation_dict:
                all_incidents_validation.update({id_: incident_validation.validation_dict})

        return all_incidents_validation

    @staticmethod
    def __validate_indicators(indicators, stix_header):
        all_indicators_validation = {}
        for indicator in indicators:
            id_ = indicator['id']
            indicator_validation = ObjectValidationInfo()
            indicator_validation.extend(CommonValidationInfo.validate(item=indicator,
                                                                      package_dict=stix_header))
            namespace_validation = NamespaceValidationInfo.validate(r'ind', id_)
            if namespace_validation.is_local():
                indicator_properties = IndicatorStructureConverter.package_to_simple(indicator, stix_header)
                indicator_validation.extend(IndicatorValidationInfo.validate(**indicator_properties))
            else:
                indicator_validation.extend(namespace_validation)
            if indicator_validation.validation_dict:
                all_indicators_validation.update({id_: indicator_validation.validation_dict})

        return all_indicators_validation

    @staticmethod
    def __validate_other(other_objects, type_, stix_header):
        all_other_objects_validation = {}
        for other_object in other_objects:
            id_ = other_object['id']
            other_object_validation = ObjectValidationInfo()
            other_object_validation.extend(CommonValidationInfo.validate(item=other_object,
                                                               package_dict=stix_header))
            namespace_validation = NamespaceValidationInfo.validate(type_, id_)
            if not namespace_validation.is_local():
                other_object_validation.extend(namespace_validation)

            if other_object_validation.validation_dict:
                all_other_objects_validation.update({id_: other_object_validation.validation_dict})

        return all_other_objects_validation

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
