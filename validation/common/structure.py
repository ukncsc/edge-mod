
from adapters.certuk_mod.validation.observable.address import AddressValidationInfo
from adapters.certuk_mod.validation.observable.socket_type import SocketValidationInfo
from adapters.certuk_mod.validation.observable.http_session import HTTPSessionValidationInfo
from adapters.certuk_mod.validation.observable.email_type import EmailValidationInfo
from adapters.certuk_mod.validation.observable.artifact import ArtifactValidationInfo
from adapters.certuk_mod.validation.observable.domain import DomainNameValidationInfo
from adapters.certuk_mod.validation.observable.registry_key import RegistryKeyValidationInfo
from adapters.certuk_mod.validation.observable.file import FileValidationInfo


class ObservableStructureConverter(object):

    @staticmethod
    def builder_to_simple(object_type, builder_dict):
        actual_object_type = ObservableStructureConverter.__get_object_type_from_builder(object_type)

        handler = ObservableStructureConverter.__get_builder_package_conversion_handler(actual_object_type)
        if handler:
            simple = handler(builder_dict)
        else:
            simple = builder_dict

        simple['object_type'] = actual_object_type
        simple.pop('objectType', None)

        return simple

    @staticmethod
    def __get_object_type_from_builder(object_type_short):
        object_type_map = {
            'Domain Name': DomainNameValidationInfo.TYPE,
            'Registry Key': RegistryKeyValidationInfo.TYPE,
            'Email': EmailValidationInfo.TYPE,
            'HTTP Session': HTTPSessionValidationInfo.TYPE,
            'Socket': SocketValidationInfo.TYPE
        }

        object_type = object_type_map.get(object_type_short)
        if not object_type:
            object_type = object_type_short + 'ObjectType'
        return object_type

    @staticmethod
    def __get_package_conversion_handler(object_type):
        conversion_handlers = {
            AddressValidationInfo.TYPE: ObservableStructureConverter.__address_package_to_simple,
            SocketValidationInfo.TYPE: ObservableStructureConverter.__socket_package_to_simple,
            HTTPSessionValidationInfo.TYPE: ObservableStructureConverter.__https_session_package_to_simple,
            EmailValidationInfo.TYPE: ObservableStructureConverter.__email_message_package_to_simple
        }
        return conversion_handlers.get(object_type)

    @staticmethod
    def __get_builder_package_conversion_handler(object_type):
        conversion_handlers = {
            ArtifactValidationInfo.TYPE: ObservableStructureConverter.__artifact_builder_to_simple,
            FileValidationInfo.TYPE: ObservableStructureConverter.__file_builder_to_simple
        }
        return conversion_handlers.get(object_type)

    @staticmethod
    def __file_builder_to_simple(builder_dict):
        simple = builder_dict.copy()
        hashes = simple.get('hashes', {})
        for hash_ in hashes:
            hash_['type'] = hash_.pop('hash_type')
            hash_['simple_hash_value'] = hash_.pop('hash_value')
        return simple

    @staticmethod
    def __artifact_builder_to_simple(builder_dict):
        simple = builder_dict.copy()
        simple['type'] = simple.pop('artifactType', None)
        simple['raw_artifact'] = simple.pop('artifactRaw', None)
        return simple

    @staticmethod
    def package_to_simple(object_type, package_dict):
        converter = ObservableStructureConverter.__get_package_conversion_handler(object_type)
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
    def __socket_package_to_simple(builder_dict):
        simple = builder_dict.copy()
        port = simple.pop('port', {})
        simple['port'] = port.get('port_value')
        simple['protocol'] = port.get('layer4_protocol')

        ip_address = simple.pop('ip_address', None)
        if ip_address:
            simple['ip_address'] = ip_address['address_value']
        hostname = simple.pop('hostname', None)
        if hostname:
            simple['hostname'] = hostname['hostname_value']

        return simple

    @staticmethod
    def __https_session_package_to_simple(package_dict):
        simple = package_dict.copy()
        try:
            http_request_response = simple.pop('http_request_response', {})
            simple['user_agent'] = \
                http_request_response[0]['http_client_request']['http_request_header']['parsed_header']['user_agent']
        except LookupError:
            simple['user_agent'] = None

        return simple

    @staticmethod
    def __email_message_package_to_simple(package_dict):
        simple = package_dict.copy()

        header = simple.pop('header', {})

        simple['subject'] = header.get('subject')
        if header.get('from'):
            simple['from'] = header['from'].get('address_value')
        simple['date'] = header.get('date')

        def flatten_address_list(address_list):
            if isinstance(address_list, list):
                return [address['address_value'] for address in address_list]
            return None

        simple['to'] = flatten_address_list(header.get('to'))
        simple['cc'] = flatten_address_list(header.get('cc'))
        simple['bcc'] = flatten_address_list(header.get('bcc'))

        return simple


class IndicatorStructureConverter(object):

    @staticmethod
    def package_to_simple(package_dict, package_header_dict):
        simple = package_dict.copy()
        try:
            simple['confidence'] = package_dict['confidence']['value']['value']
        except KeyError:
            simple['confidence'] = None

        try:
            kill_chain_phases = simple.pop('kill_chain_phases', {})
            simple['phase_id'] = kill_chain_phases['kill_chain_phases'][0]['phase_id']
        except LookupError:
            simple['phase_id'] = None

        try:
            handling_structures = package_dict['handling']
            marking_structure = handling_structures[0]['marking_structures'][0]
            simple['tlp'] = marking_structure['color']
        except LookupError:
            try:
                handling_structures = package_header_dict['handling']
                marking_structure = handling_structures[0]['marking_structures'][0]
                simple['tlp'] = marking_structure['color']
            except LookupError:
                simple['tlp'] = None

        try:
            simple['suggested_coas'] = simple['suggested_coas']['suggested_coas']
        except KeyError:
            simple['suggested_coas'] = None

        return simple

    @staticmethod
    def builder_to_simple(builder_dict):
        simple = builder_dict.copy()
        simple['indicator_types'] = simple.pop('indicatorType', None)
        simple['observable'] = simple.pop('observables', None)
        simple['phase_id'] = simple.pop('kill_chain_phase', None)

        return simple


class OtherStructureConverter(object):

    @staticmethod
    def package_to_simple(package_dict, package_header_dict):
        simple = package_dict.copy()
        try:
            handling_structures = package_dict['handling']
            marking_structure = handling_structures[0]['marking_structures'][0]
            simple['tlp'] = marking_structure['color']
        except LookupError:
            try:
                if not package_header_dict:
                    raise LookupError("package header not found")
                handling_structures = package_header_dict['handling']
                marking_structure = handling_structures[0]['marking_structures'][0]
                simple['tlp'] = marking_structure['color']
            except LookupError:
                simple['tlp'] = None

        return simple
