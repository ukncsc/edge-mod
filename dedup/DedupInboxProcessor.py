from edge.inbox import InboxProcessorForPackages, InboxProcessorForBuilders, InboxItem, InboxError, anti_ping_pong
from edge.generic import create_package, EdgeObject
from mongoengine.connection import get_db
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from .edges import dedup_collections


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


def existing_hash_dedup(contents, hashes, user):
    db = get_db()

    existing_items = db.stix.find({
        'data.hash': {
            '$in': hashes.values()
        }
    }, {
        '_id': 1,
        'data.hash': 1
    })

    hash_to_existing_ids = {doc['data']['hash']: doc['_id'] for doc in existing_items}

    maptable = {
        id_: hash_to_existing_ids[hash_] for id_, hash_ in hashes.iteritems() if hash_ in hash_to_existing_ids
    }

    out, additional_sightings = coalesce_duplicates_to_sitings(contents, maptable)

    update_sighting_counts(additional_sightings, user)

    message = generate_message("Remapped %d objects to existing objects based on hashes", contents, out)

    return out, message


def new_hash_dedup(contents, hashes, user):
    hash_to_ids = {}
    for id_, hash_ in sorted(hashes.iteritems()):
        hash_to_ids.setdefault(hash_, []).append(id_)

    maptable = {}
    for hash_, ids in hash_to_ids.iteritems():
        if len(ids) > 1:
            master = ids[0]
            for dup in ids[1:]:
                maptable[dup] = master

    out, additional_sightings = coalesce_duplicates_to_sitings(contents, maptable)

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
