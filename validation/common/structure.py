from adapters.certuk_mod.validation.observable.address import AddressValidationInfo
from adapters.certuk_mod.validation.observable.socket_type import SocketValidationInfo
from adapters.certuk_mod.validation.observable.http_session import HTTPSessionValidationInfo
from adapters.certuk_mod.validation.observable.email_type import EmailValidationInfo
from adapters.certuk_mod.validation.observable.artifact import ArtifactValidationInfo
from adapters.certuk_mod.validation.observable.registry_key import RegistryKeyValidationInfo
from adapters.certuk_mod.validation.observable.uri import URIValidationInfo
from adapters.certuk_mod.validation.observable.domain import DomainNameValidationInfo
from adapters.certuk_mod.validation.observable.file import FileValidationInfo
from adapters.certuk_mod.validation.observable.hostname import HostnameValidationInfo
from adapters.certuk_mod.validation.observable.mutex import MutexValidationInfo
from adapters.certuk_mod.validation.observable.network_connection import NetworkConnectionValidationInfo


class ObservableStructureConverter(object):
    @staticmethod
    def flatten_property_value_field(object_):
        if isinstance(object_, dict):
            return object_.get('value', object_)
        return object_

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
            'Socket': SocketValidationInfo.TYPE,
            'Network Connection': NetworkConnectionValidationInfo.TYPE
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
            EmailValidationInfo.TYPE: ObservableStructureConverter.__email_message_package_to_simple,
            URIValidationInfo.TYPE: ObservableStructureConverter.__url_package_to_simple,
            DomainNameValidationInfo.TYPE: ObservableStructureConverter.__domain_package_to_simple,
            FileValidationInfo.TYPE: ObservableStructureConverter.__file_package_to_simple,
            ArtifactValidationInfo.TYPE: ObservableStructureConverter.__artifact_package_to_simple,
            HostnameValidationInfo.TYPE: ObservableStructureConverter.__hostname_package_to_simple,
            MutexValidationInfo.TYPE: ObservableStructureConverter.__mutex_package_to_simple,
            RegistryKeyValidationInfo.TYPE: ObservableStructureConverter.__registry_key_package_to_simple,
            NetworkConnectionValidationInfo.TYPE: ObservableStructureConverter.__network_connection_package_to_simple
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
    def __domain_package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['value'] = ObservableStructureConverter.flatten_property_value_field(simple.get('value'))
        return simple

    @staticmethod
    def __mutex_package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['name'] = ObservableStructureConverter.flatten_property_value_field(simple.get('name'))
        return simple

    @staticmethod
    def __registry_key_package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['hive'] = ObservableStructureConverter.flatten_property_value_field(simple.get('hive'))
        simple['key'] = ObservableStructureConverter.flatten_property_value_field(simple.get('key'))
        return simple

    @staticmethod
    def __hostname_package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['hostname_value'] = ObservableStructureConverter.flatten_property_value_field(
            simple.get('hostname_value'))
        return simple

    @staticmethod
    def __artifact_package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['raw_artifact'] = ObservableStructureConverter.flatten_property_value_field(
            simple.get('raw_artifact'))
        return simple

    @staticmethod
    def __file_package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['size_in_bytes'] = ObservableStructureConverter.flatten_property_value_field(
            simple.get('size_in_bytes'))
        simple['file_extension'] = ObservableStructureConverter.flatten_property_value_field(
            simple.get('file_extension'))
        hashes = simple.get('hashes', {})
        for hash_ in hashes:
            hash_['type'] = ObservableStructureConverter.flatten_property_value_field(hash_.get('type'))
            hash_['simple_hash_value'] = ObservableStructureConverter.flatten_property_value_field(hash_.get('simple_hash_value'))
        return simple

    @staticmethod
    def __url_package_to_simple(package_dict):
        simple = package_dict.copy()
        simple['value'] = ObservableStructureConverter.flatten_property_value_field(simple.get('value'))
        return simple

    @staticmethod
    def __address_package_to_simple(package_dict):
        # This doesn't handle more exotic structures like IP ranges...
        simple = package_dict.copy()
        simple['address_value'] = ObservableStructureConverter.flatten_property_value_field(
            simple.get('address_value'))
        return simple

    @staticmethod
    def __socket_package_to_simple(builder_dict):
        simple = builder_dict.copy()
        port = simple.pop('port', {})
        simple['port'] = ObservableStructureConverter.flatten_property_value_field(port.get('port_value'))
        simple['protocol'] = ObservableStructureConverter.flatten_property_value_field(
            port.get('layer4_protocol'))

        ip_address = simple.pop('ip_address', None)
        if ip_address:
            simple['ip_address'] = ObservableStructureConverter.flatten_property_value_field(
                ip_address.get('address_value'))
        hostname = simple.pop('hostname', None)
        if hostname:
            simple['hostname'] = ObservableStructureConverter.flatten_property_value_field(
                hostname.get('hostname_value'))

        return simple

    @staticmethod
    def __network_connection_package_to_simple(builder_dict):
        simple = builder_dict.copy()
        simple['source_socket_address'] = \
            ObservableStructureConverter.__socket_package_to_simple(simple.pop('source_socket_address', {}))
        simple['destination_socket_address'] = \
            ObservableStructureConverter.__socket_package_to_simple(simple.pop('destination_socket_address', {}))
        return simple

    @staticmethod
    def __https_session_package_to_simple(package_dict):
        simple = package_dict.copy()
        try:
            http_request_response = simple.pop('http_request_response', {})
            simple['user_agent'] = \
                ObservableStructureConverter.flatten_property_value_field(
                    http_request_response[0]['http_client_request']
                    ['http_request_header']['parsed_header']['user_agent'])
        except LookupError:
            simple['user_agent'] = None

        return simple

    @staticmethod
    def __email_message_package_to_simple(package_dict):
        simple = package_dict.copy()

        header = simple.pop('header', {})

        simple['subject'] = ObservableStructureConverter.flatten_property_value_field(header.get('subject'))
        if header.get('from'):
            simple['from'] = ObservableStructureConverter.flatten_property_value_field(
                header['from'].get('address_value'))
        simple['date'] = ObservableStructureConverter.flatten_property_value_field(header.get('date'))

        def flatten_address_list(address_list):
            if isinstance(address_list, list):
                return [ObservableStructureConverter.flatten_property_value_field(address.get('address_value'))
                        for address
                        in address_list]
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
