import hashlib

from edge.generic import WHICH_DBOBJ, HASH_DISPATCH
from edge.observable import \
    CYBOX_SHORT_DESCRIPTION, \
    DBObservable, \
    get_obs_value as original_get_obs_value, \
    get_obs_type as original_get_obs_type, \
    get_obs_title as original_get_obs_title, \
    get_obs_description as original_get_obs_description
from edge.tools import rgetattr, dicthash_sha1, scrubcopy, nested_get

OBS_HASH_PATHS = {
    'AddressObjectType': ['category', 'address_value'],
    'ArtifactObjectType': ['type_', 'data'],
    'DomainNameObjectType': ['type_', 'value'],
    'HostnameObjectType': ['hostname_value'],
    'MutexObjectType': ['name'],
    'SocketAddressObjectType': ['ip_address', 'hostname.hostname_value', 'port.layer4_protocol', 'port.port_value'],
    'URIObjectType': ['type_', 'value'],
    'WindowsRegistryKeyObjectType': ['key', 'hive'],
}


def generate_db_observable_patch(custom_draft_handler_map):
    class DBObservablePatch(DBObservable):
        def __init__(self, obj=None, item=None, id_=None):
            super(DBObservablePatch, self).__init__(obj, item, id_)

        CUSTOM_DRAFT_HANDLERS = custom_draft_handler_map

        @staticmethod
        def _get_custom_to_draft_handler(object_type):
            try:
                return DBObservablePatch.CUSTOM_DRAFT_HANDLERS[object_type]
            except KeyError:
                raise ValueError("Unexpected Object Type %s" % object_type)

        @classmethod
        def to_draft(cls, observable, tg, load_by_id, id_ns=''):
            try:
                draft = super(DBObservablePatch, cls).to_draft(observable, tg, load_by_id, id_ns=id_ns)
                # When creating a draft from a fully formed object with None for some fields, the draft contains
                # fields with string 'None' which can cause parsing issues e.g. vlan_num
                for attr, value in draft.iteritems():
                    if value == 'None':
                        draft[attr] = ''

                # to_draft sets the hash_type to lower case. This is not what is expected during Inboxing or Validation!
                hash_type_map = {'md5': 'MD5', 'md6': 'MD6', 'sha1': 'SHA1', 'sha224': 'SHA224',
                                 'sha256': 'SHA256', 'sha384': 'SHA384', 'sha512': 'SHA512',
                                 'ssdeep': 'SSDEEP', 'other': 'Other'}

                if 'hashes' in draft:
                    for hash_ in draft['hashes']:
                        hash_['hash_type'] = hash_type_map.get(hash_['hash_type'].lower(), 'Other')

                return draft
            except ValueError, v:
                if v.__class__ != ValueError:
                    raise

            object_type = rgetattr(observable, ['_object', '_properties', '_XSI_TYPE'], 'None')
            draft_handler = DBObservablePatch._get_custom_to_draft_handler(object_type)
            return draft_handler(observable, tg, load_by_id, id_ns)

        @classmethod
        def dupehash(cls, apiobj):
            properties = rgetattr(apiobj, ['object_', 'properties'], None)
            obs_type = rgetattr(properties, ['_XSI_TYPE'], None)
            if obs_type is not None:
                if obs_type in OBS_HASH_PATHS:
                    # we can produce a meaningful hash for selected properties
                    to_hash = "%s|%s|%s" % (
                        cls.SHORT_NAME,
                        obs_type,
                        '|'.join(
                            [str(rgetattr(properties, str(path).split('.'), '')) for path in
                             OBS_HASH_PATHS[obs_type]]
                        )
                    )
                    hash_ = "certuk:%s" % hashlib.sha1(to_hash).hexdigest()
                else:
                    # we can't produce a meaningful hash on selected properties, so hash them all
                    to_hash = scrubcopy(nested_get(apiobj.to_dict(), ['object', 'properties'], {}), ['xsi:type'])
                    hash_ = "certuk:%s" % dicthash_sha1(to_hash, salt=cls.SHORT_NAME)
            else:
                # we don't know what this is, so let the existing code deal with it
                hash_ = super(DBObservablePatch, cls).dupehash(apiobj)

            return hash_

    return DBObservablePatch


def generate_custom_get_obs_value(custom_object_value_map):
    def custom_get_obs_value(obj):
        type_ = rgetattr(obj, ['object_', 'properties', '_XSI_TYPE'], None)
        custom_type_handler = custom_object_value_map.get(type_)
        if custom_type_handler is None:
            return original_get_obs_value(obj)
        return custom_type_handler(obj)

    return custom_get_obs_value


def apply_patch(custom_observable_definitions):
    custom_draft_handler_map = {}
    custom_summary_value_map = {}

    for definition in custom_observable_definitions:
        custom_draft_handler_map[definition.object_type] = definition.to_draft_handler
        custom_summary_value_map[definition.object_type] = definition.summary_value_generator
        CYBOX_SHORT_DESCRIPTION[definition.object_type] = definition.human_readable_type

    DBObservable.SUMMARY_BINDING = (
        ('type', original_get_obs_type),
        ('title', original_get_obs_title),
        ('description', original_get_obs_description),
        ('value', generate_custom_get_obs_value(custom_summary_value_map)),
    )

    db_observable_patch = generate_db_observable_patch(custom_draft_handler_map)
    WHICH_DBOBJ['obs'] = db_observable_patch
    HASH_DISPATCH['obs'] = db_observable_patch.dupehash
