from cybox.objects.network_connection_object import NetworkConnection
from cybox.objects.socket_address_object import SocketAddress, Port
from cybox.objects.address_object import Address
from cybox.objects.hostname_object import Hostname
from edge.tools import rgetattr
from adapters.certuk_mod.builder.custom_observable_definition import CustomObservableDefinition
from indicator.observable_object_generator import ObservableObjectGenerator

class NetworkConnectionObservableDefinition(CustomObservableDefinition):

    def __init__(self):
        super(NetworkConnectionObservableDefinition, self).__init__(
            object_type='NetworkConnectionObjectType',
            human_readable_type='Network Connection',
            can_batch_create=False,
            custom_id_prefix='network_connection',
            builder_to_stix_object=NetworkConnectionObservableDefinition.builder_to_stix_object,
            summary_value_generator=NetworkConnectionObservableDefinition.summary_value_generator,
            to_draft_handler=NetworkConnectionObservableDefinition.to_draft_handler
        )

    def builder_to_stix_object(self, object_data):
        network_connection = NetworkConnection()

        src_socket_address = ObservableObjectGenerator._generate_socket_object(object_data['source_socket_address'])
        dst_socket_address = ObservableObjectGenerator._generate_socket_object(object_data['destination_socket_address'])

        network_connection.source_socket_address = src_socket_address
        network_connection.destination_socket_address = dst_socket_address

        return network_connection

    def get_socket_description(self, socket_object):
        address = rgetattr(socket_object, ['ip_address', 'address_value'], '')
        hostname = rgetattr(socket_object, ['hostname', 'hostname_value'], '')
        port = rgetattr(socket_object, ['port', 'port_value'], '')
        protocol = rgetattr(socket_object, ['port', 'layer4protocol'], '')

        if address:
            combined = str(address)
        elif hostname:
            combined = str(hostname)
        else:
            combined = '(unknown)'

        if port:
            combined += str(port)
        if protocol:
            combined += str(protocol)

        return str(combined)

    def summary_value_generator(self, obj):
        network_connection_object = "Source Socket Address: "
        network_connection_object += self.get_socket_description(rgetattr(obj, ['_object', 'properties', 'source_socket_address']))
        network_connection_object += " Destination Socket Address: "
        network_connection_object += self.get_socket_description(rgetattr(obj, ['_object', 'properties', 'destination_socket_address']))
        return network_connection_object

    def to_draft_handler(self, observable, tg, load_by_id, id_ns=''):
        return {
            'objectType': 'Network Connection',
            'id': rgetattr(observable, ['id_'], ''),
            'id_ns': id_ns,
            'title': rgetattr(observable, ['title'], ''),
            'description': str(rgetattr(observable, ['description'], '')),
            'network_connection': self.summary_value_generator(observable)
        }
