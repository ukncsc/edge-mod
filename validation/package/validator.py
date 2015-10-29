
from edge.combine import STIXPackage
import json
from ..observable.validator import ObservableValidator


class PackageValidationInfo(object):

    def __init__(self, package_dict):
        self.package_dict = package_dict
        self.validation_dict = PackageValidationInfo.__generate_validation_dict(package_dict)

    @staticmethod
    def __generate_validation_dict(package_dict):
        validation = {}
        validation.update(PackageValidationInfo.__validate_observables(package_dict))
        # and other types...
        return validation

    @staticmethod
    def __validate_observables(package_dict):
        observables = package_dict['observables']['observables']
        observable_validation = {}
        for observable in observables:
            if 'observable_composition' not in observable:
                properties = observable['object']['properties']
                id_ = observable['id']
                validation_results = ObservableValidator.validate(object_type=properties['xsi:type'], **properties)
                if validation_results and validation_results.validation_dict:
                    observable_validation.update({id_: validation_results.validation_dict})
        return observable_validation

    @staticmethod
    def __validate_indicators(package_dict):
        pass

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
