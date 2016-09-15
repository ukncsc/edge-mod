import random
from django.conf import settings
from adapters.certuk_mod.catalog.generate_snort import generate_sid

cfg = settings.ACTIVE_CONFIG
LOCAL_ALIAS = cfg.by_key('company_alias')


def write_bro_rule(src_IP="*", dst_IP="*", src_port="*", dst_port="*", proto="*"):
    return "signature { protocol == %s src-ip == %s src-port == %s  dst-ip == %s dst-port == %s}" % \
           (proto, src_IP, src_port, dst_IP, dst_port);


def generate_bro(obs, obs_type, ref):
    if obs_type == 'AddressObjectType':
        return write_bro_rule(dst_IP=obs)

    if obs_type == "NetworkConnectionObjectType":
        # needs to be smarter deadling with non existing values, even in cert data no guarantee all values there so order is messed
        content_string = ''
        parsed_network_connection = obs.split(':')
        src_ip = parsed_network_connection[1]
        src_prt = parsed_network_connection[2]
        protocol = parsed_network_connection[3]
        dst_ip = parsed_network_connection[4]

        return ""  # write_bro_rule()

    if obs_type == "SocketAddressObjectType":

        content_string = ''
        parsed_socket = obs.split(':')
        src_ip = parsed_socket[0]
        parsed_port_and_protocol = parsed_socket[1].split('(')
        if len(parsed_port_and_protocol) > 1:
            src_prt = parsed_port_and_protocol[0]
            protocol = parsed_port_and_protocol[1].strip(')')
        else:
            src_prt = parsed_port_and_protocol[0]
            protocol = "*"

        return write_bro_rule(proto=protocol, src_IP=src_ip, src_port=src_prt)

    return ''
