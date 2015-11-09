
from ..observable.address import AddressValidationInfo
from ..observable.socket_type import SocketValidationInfo


class ObservableStructureConverter(object):

    @staticmethod
    def __get_conversion_handler(object_type):
        conversion_handlers = {
            AddressValidationInfo.TYPE: ObservableStructureConverter.__address_package_to_simple,
            SocketValidationInfo.TYPE: ObservableStructureConverter.__socket_package_to_simple
        }
        return conversion_handlers.get(object_type)

    @staticmethod
    def package_to_simple(object_type, package_dict):
        converter = ObservableStructureConverter.__get_conversion_handler(object_type)
        if converter:
            return converter(package_dict)
        return package_dict

    @staticmethod
    def __address_package_to_simple(package_dict):
        # This doesn't handle more exotic structures like IP ranges...
        simple = package_dict.copy()
        address_value = simple['address_value']
        if isinstance(address_value, dict):
            simple['address_value'] = address_value['value']
        return simple

    @staticmethod
    def __socket_package_to_simple(package_dict):
        simple = {
            'port': package_dict['port']['port_value'],
            'protocol': package_dict['port']['layer4_protocol']
        }
        if package_dict.get('ip_address'):
            simple['ip_address'] = package_dict['ip_address']['address_value']
        if package_dict.get('hostname'):
            simple['hostname'] = package_dict['hostname']['hostname_value']

        return simple


class IndicatorStructureConverter(object):

    @staticmethod
    def package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['confidence'] = package_dict['confidence']['value']['value']
        try:
            handling_structures = package_dict['handling']
            marking_structure = handling_structures[0]['marking_structures'][0]
            simple['tlp'] = marking_structure['color']
        except LookupError:
            simple['tlp'] = None

        return simple
