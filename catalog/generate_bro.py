from django.conf import settings

from cybox.objects.address_object import Address
from cybox.objects.uri_object import URI

cfg = settings.ACTIVE_CONFIG
LOCAL_ALIAS = cfg.by_key('company_alias')

OBJECT_FIELDS = {
    'AddressObjectType': ['address_value'],
    'DomainNameObjectType': ['value'],
    'EmailMessageObjectType': [
        'header.from_.address_value',
        'header.to.address_value',
    ],
    'FileObjectType': ['hashes.simple_hash_value'],
    'HTTPSessionObjectType': ['http_request_response.http_client_request.' +
                    'http_request_header.parsed_header.user_agent'],
    'SocketAddressObjectType': ['ip_address.address_value'],
    'URIObjectType': ['value'],
}

OBJECT_CONSTRAINTS = {
    'Address': {
        'category': [Address.CAT_IPV4, Address.CAT_IPV6],
    },
    'URI': {
        'type_': [URI.TYPE_URL],
    },
}

STRING_CONDITION_CONSTRAINT = ['None', 'Equals']

HEADER_LABELS = [
    'indicator', 'indicator_type', 'meta.source', 'meta.url',
    'meta.do_notice', 'meta.if_in', 'meta.whitelist',
]

# Map Cybox object type to Bro Intel types.
BIF_TYPE_MAPPING = {
    'AddressObjectType': 'Intel::ADDR',
    'DomainNameObjectType': 'Intel::DOMAIN',
    'EmailMessageObjectType': 'Intel::EMAIL',
    'FileObjectType': 'Intel::FILE_HASH',
    'HTTPSessionObjectType': 'Intel::SOFTWARE',
    'SocketAddressObjectType': 'Intel::ADDR',
    'URIObjectType': 'Intel::URL',
}

# Map observable id prefix to source and url.
BIF_SOURCE_MAPPING = {
    'cert_au': {
        'source': 'CERT-AU',
        'url': 'https://www.cert.gov.au/',
    },
    'CCIRC-CCRIC': {
        'source': 'CCIRC',
        'url': ('https://www.publicsafety.gc.ca/' +
                'cnt/ntnl-scrt/cbr-scrt/ccirc-ccric-eng.aspx'),
    },
    'NCCIC': {
        'source': 'NCCIC',
        'url': 'https://www.us-cert.gov/',
    },
}


def generate_bro(obs, obs_type, id_prefix):
    # Deals with nested structure for fields which have attributes
    def flatten_nested_values(obj):
        if isinstance(obj,dict):
            return obj["value"]
        else:
            return obj

    text=''
    if obs_type in BIF_TYPE_MAPPING:
        # Look up source and url from observable ID
        if id_prefix in BIF_SOURCE_MAPPING:
            source = BIF_SOURCE_MAPPING[id_prefix]['source']
            url = BIF_SOURCE_MAPPING[id_prefix]['url']
        else:
            source = id_prefix
            url = ''

        bif_type = BIF_TYPE_MAPPING[obs_type]
        for fields in obs:
            for field in OBJECT_FIELDS[obs_type]:
                if field in fields:
                    field_values = [
                        flatten_nested_values(obs[field]),
                        '\t',
                        bif_type,
                        '\t',
                        source,
                        '\t',
                        url,
                        '\t',
                        'T',
                        '\t',
                        '-',
                        '\t',
                        '-',
                    ]
                    text += text.join(field_values)
    return text

