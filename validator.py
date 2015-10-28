
from edge.combine import STIXPackage
import json


class ValidationStatus(object):
    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"


class ObservableValidator(object):

    def __init__(self):
        self.__observableTypeValidation = {
            'AddressObjectType': self.__validate_address
        }

    def validate(self, properties):
        handler = self.__observableTypeValidation.get(properties.get('xsi:type'))
        if handler is not None:
            return handler(properties)

    @staticmethod
    def __validate_address(address_properties):
        # in practice, check value according to category....
        if 'address_value' in address_properties:
            return {
                'address_value': {
                    'status': ValidationStatus.WARN,
                    'message': 'This is a dummy validation message :)'
                }
            }


class PackageValidationInfo(object):

    Observables = ObservableValidator()

    def __init__(self, package_dict):
        self.package_dict = package_dict
        self.validation_dict = PackageValidationInfo.__generate_validation_dict(package_dict)
        self.overall_status = PackageValidationInfo.__get_overall_status(self.validation_dict)

    @staticmethod
    def __get_overall_status(validation_dict):
        # Actually do something...
        return ValidationStatus.WARN

    @staticmethod
    def __generate_validation_dict(package_dict):
        validation = {}
        validation.update(PackageValidationInfo.__validate_observables(package_dict))
        # and other types...
        return validation


    @staticmethod
    def __validate_observables(package_dict):
        observables = package_dict['observables']['observables']
        validation_results = {}
        for observable in observables:
            if 'observable_composition' not in observable:
                properties = observable['object']['properties']
                id_ = observable['id']
                validation_info = PackageValidationInfo.Observables.validate(properties)
                if validation_info is not None:
                    validation_results.update({id_: validation_info})
        return validation_results

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
