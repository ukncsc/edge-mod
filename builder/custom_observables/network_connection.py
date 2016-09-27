from cybox.objects.network_connection_object import NetworkConnection
from edge.tools import rgetattr
from adapters.certuk_mod.builder.custom_observable_definition import CustomObservableDefinition
from indicator.observable_object_generator import ObservableObjectGenerator


class NetworkConnectionObservableDefinition(CustomObservableDefinition):

    def __init__(self):
        super(NetworkConnectionObservableDefinition, self).__init__(
            object_type='NetworkConnectionObjectType',
            human_readable_type='Network Connection',
            can_batch_create=False,
            custom_id_prefix='network_connection'
        )

    def builder_to_stix_object(self, object_data):
        network_connection = NetworkConnection()

        src_socket_address = ObservableObjectGenerator._generate_socket_object(object_data['source_socket_address'])
        dst_socket_address = ObservableObjectGenerator._generate_socket_object(
            object_data['destination_socket_address'])

        network_connection.source_socket_address = src_socket_address
        network_connection.destination_socket_address = dst_socket_address

        return network_connection

    def get_socket(self, socket_object):
        address = rgetattr(socket_object, ['ip_address', 'address_value'], '')
        hostname = rgetattr(socket_object, ['hostname', 'hostname_value'], '')
        port = rgetattr(socket_object, ['port', 'port_value'], '')
        protocol = rgetattr(socket_object, ['port', 'layer4_protocol'], '')

        socket = {
            "ip_address": str(address),
            "hostname": str(hostname),
            "port": str(port),
            "protocol": str(protocol)
        }
        return socket

    def get_socket_summary(self, socket_object):
        socket = self.get_socket(socket_object)

        if socket['ip_address']:
            combined = str(socket['ip_address'])
        elif socket['hostname']:
            combined = str(socket['hostname'])
        else:
            combined = '(unknown)'

        if socket['port']:
            combined += ":"
            combined += str(socket['port'])
        if socket['protocol']:
            combined += ":"
            combined += str(socket['protocol'])

        return str(combined)

    def summary_value_generator(self, obj):
        network_connection_object = "Source Socket Address: "
        network_connection_object += self.get_socket_summary(
            rgetattr(obj, ['_object', 'properties', 'source_socket_address']))
        network_connection_object += ": Destination Socket Address: "
        network_connection_object += self.get_socket_summary(
            rgetattr(obj, ['_object', 'properties', 'destination_socket_address']))
        return network_connection_object

    def to_draft_handler(self, observable, tg, load_by_id, id_ns=''):
        return {
            'objectType': 'Network Connection',
            'id': rgetattr(observable, ['id_'], ''),
            'id_ns': id_ns,
            'title': rgetattr(observable, ['title'], ''),
            'description': str(rgetattr(observable, ['description'], '')),
            'source_socket_address': self.get_socket(
                rgetattr(observable, ['_object', 'properties', 'source_socket_address'])),
            'destination_socket_address': self.get_socket(
                rgetattr(observable, ['_object', 'properties', 'destination_socket_address']))
        }
