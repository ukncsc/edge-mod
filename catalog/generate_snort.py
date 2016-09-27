import random
from django.conf import settings

cfg = settings.ACTIVE_CONFIG
LOCAL_ALIAS = cfg.by_key('company_alias')


def write_snort_rule(src_ip, dst_ip, src_port, dst_port, proto, msg, sid, detail):
    return "alert %s %s %s -> %s %s (msg:\"%s\";%s sid: %s;)" % \
           (proto, src_ip, src_port, dst_ip, dst_port, msg, detail, sid)


def generate_sid():
    return '200' + "%0.5d" % random.randint(0, 99999)


def generate_snort(obs, obs_type, ref):
    if obs_type == 'AddressObjectType':
        msg = ('[%s] Automated SNORT deployment - ' % LOCAL_ALIAS) + ref
        return write_snort_rule('$HOME_NET', obs, 'any', 'any', 'tcp', msg, generate_sid(), '')

    if obs_type == 'DomainNameObjectType':
        msg = ('[%s] Automated SNORT deployment - ' % LOCAL_ALIAS) + ref

        content_string = ''
        parsed_domain = obs.split('.')
        if parsed_domain[0] == 'www':
            parsed_domain.pop(0)
        for item in parsed_domain:
            content_string = content_string + '|' + str(len(item)).zfill(2) + '|' + item
        detail = 'content:"' + content_string + '|00|";'
        return write_snort_rule('$HOME_NET', 'any', '53', 'any', 'udp', msg, generate_sid(), detail)

    return ''
