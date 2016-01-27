import pymongo

from edge.inbox import InboxProcessorForPackages, InboxProcessorForBuilders, InboxItem, InboxError, anti_ping_pong
from edge.generic import create_package, EdgeObject
from mongoengine.connection import get_db
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from edge.tools import rgetattr
from .edges import dedup_collections

PROPERTY_FILENAME = ['api_object', 'obj', 'object_', 'properties', 'file_name']
PROPERTY_MD5 = ['api_object', 'obj', 'object_', 'properties', 'md5']
PROPERTY_SHA1 = ['api_object', 'obj', 'object_', 'properties', 'sha1']
PROPERTY_SHA256 = ['api_object', 'obj', 'object_', 'properties', 'sha256']


def get_sighting_count(obs):
    sighting_count = getattr(obs, 'sighting_count', 1)
    if sighting_count is None:
        sighting_count = 1
    return sighting_count


def update_sighting_counts(additional_sightings, user):
    inbox_processor = InboxProcessorForBuilders(user=user)
    for id_, count in additional_sightings.iteritems():
        edge_object = EdgeObject.load(id_)
        api_object = edge_object.to_ApiObject()
        api_object.obj.sighting_count = get_sighting_count(api_object.obj) + count
        inbox_processor.add(InboxItem(
            api_object=api_object,
            etlp=edge_object.etlp,
            etou=edge_object.etou,
            esms=edge_object.esms
        ))
    inbox_processor.run()


def coalesce_duplicates_to_sitings(contents, maptable):
    out = {}
    additional_sightings = {}
    for id_, io in contents.iteritems():
        if id_ not in maptable:
            io.api_object = io.api_object.remap(maptable)
            out[id_] = io
        elif io.api_object.ty == 'obs':
            existing_id = maptable[id_]
            sightings_for_duplicate = get_sighting_count(io.api_object.obj)
            additional_sightings[existing_id] = additional_sightings.get(existing_id, 0) + sightings_for_duplicate
    return out, additional_sightings


def generate_message(template_text, contents, out):
    removed = len(contents) - len(out)
    message = (template_text % removed) if removed else None
    return message


def find_matching_db_file_obs(db, new_file_obs):
    def extract_properties(inbox_items, property_path):
        return list({str(rgetattr(inbox_item, property_path, None)) for inbox_item in inbox_items.itervalues()
                     if rgetattr(inbox_item, property_path, None) is not None})

    new_filenames = extract_properties(new_file_obs, PROPERTY_FILENAME)
    new_md5s = extract_properties(new_file_obs, PROPERTY_MD5)
    new_sha1s = extract_properties(new_file_obs, PROPERTY_SHA1)
    new_sha256s = extract_properties(new_file_obs, PROPERTY_SHA256)
    existing_file_obs = db.stix.find({
        'type': 'obs',
        'data.api.object.properties.xsi:type': 'FileObjectType',
        '$or': [
            {
                'data.api.object.properties.file_name': {'$in': new_filenames}
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'MD5'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_md5s}}
                ]
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'SHA1'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_sha1s}}
                ]
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'SHA256'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_sha256s}}
                ]
            }
        ]
    }).sort('created_on', pymongo.DESCENDING)
    return existing_file_obs


def is_matching_file(existing_file, new_file):
    def matches(existing, new, property_path):
        return rgetattr(existing, property_path, '') == rgetattr(new, property_path, '')

    return matches(existing_file, new_file, PROPERTY_FILENAME) and (
        matches(existing_file, new_file, PROPERTY_MD5) or
        matches(existing_file, new_file, PROPERTY_SHA1) or
        matches(existing_file, new_file, PROPERTY_SHA256)
    )


def add_matching_file_observables(db, map_table, contents):
    # identify file observables in contents excluding any which are already in map_table
    new_file_obs = {id_: inbox_item for (id_, inbox_item) in contents.iteritems()
                    if inbox_item.api_object.ty == 'obs' and
                    id_ not in map_table and  # exclude perfect matches which have already been discovered via data hash
                    rgetattr(inbox_item, ['api_object', 'obj', 'object_', 'properties', '_XSI_TYPE'],
                             None) == 'FileObjectType'}
    if not new_file_obs:
        # if we have no new file observables, we can bail out
        return

    existing_file_obs = find_matching_db_file_obs(db, new_file_obs)
    if not existing_file_obs:
        # if we have no matching existing file observables, we can bail out
        return

    for existing_file in existing_file_obs:
        for (new_id, new_file) in new_file_obs.iteritems():
            if is_matching_file(EdgeObject(existing_file).to_ApiObject(), new_file.api_object):
                map_table[new_id] = existing_file['_id']


def existing_hash_dedup(contents, hashes, user):
    db = get_db()

    existing_items = db.stix.find({
        'type': 'obs',
        'data.hash': {
            '$in': hashes.values()
        }
    }, {
        '_id': 1,
        'data.hash': 1
    }).sort('created_on', pymongo.DESCENDING)

    hash_to_existing_ids = {doc['data']['hash']: doc['_id'] for doc in existing_items}

    map_table = {
        id_: hash_to_existing_ids[hash_] for id_, hash_ in hashes.iteritems() if hash_ in hash_to_existing_ids
    }

    # file observable have more complex rules for duplicates, so simple hash matching isn't good enough
    add_matching_file_observables(db, map_table, contents)

    out, additional_sightings = coalesce_duplicates_to_sitings(contents, map_table)

    if additional_sightings:
        update_sighting_counts(additional_sightings, user)

    message = generate_message("Remapped %d objects to existing objects based on hashes", contents, out)

    return out, message


def new_hash_dedup(contents, hashes, user):
    hash_to_ids = {}
    for id_, hash_ in sorted(hashes.iteritems()):
        hash_to_ids.setdefault(hash_, []).append(id_)

    map_table = {}
    for hash_, ids in hash_to_ids.iteritems():
        if len(ids) > 1:
            master = ids[0]
            for dup in ids[1:]:
                map_table[dup] = master

    out, additional_sightings = coalesce_duplicates_to_sitings(contents, map_table)

    for id_, count in additional_sightings.iteritems():
        inbox_item = contents.get(id_, None)
        if inbox_item is not None:
            api_object = inbox_item.api_object
            api_object.obj.sighting_count = get_sighting_count(api_object.obj) + count

    message = generate_message("Merged %d objects in the supplied package based on hashes", contents, out)

    for id_, io in out.iteritems():
        dedup_collections(io.api_object.ty, io.api_object.obj)

    return out, message


class DedupInboxProcessor(InboxProcessorForPackages):
    filters = [
        anti_ping_pong,  # removes existing STIX objects matched by id
        existing_hash_dedup,  # removes existing STIX objects matched by hash
        new_hash_dedup  # removes new STIX objects matched by hash
    ]

    def __init__(self, user, trustgroups=None, streams=None):
        super(DedupInboxProcessor, self).__init__(user, trustgroups, streams)
        self.validation_result = {}

    @staticmethod
    def validate(contents):
        if not contents:
            return None
        # At this point, only things that don't already exist in the database will be in contents...
        # We can exclude packages, as they only serve as containers for other objects.
        contents_to_validate = {
            id_: inbox_item.api_object for id_, inbox_item in contents.iteritems() if inbox_item.api_object.ty != 'pkg'
        }
        # Wrap the contents in a package for convenience so they can be easily validated:
        package_for_validation = create_package(contents_to_validate)
        validation_result = PackageValidationInfo.validate(package_for_validation)

        return validation_result.validation_dict

    def apply_filters(self):
        super(DedupInboxProcessor, self).apply_filters()
        self.validation_result = DedupInboxProcessor.validate(self.contents)
        for id_, object_fields in self.validation_result.iteritems():
            for field_name in object_fields:
                if object_fields[field_name]['status'] == ValidationStatus.ERROR:
                    raise InboxError('Validation failed')
