from edge.inbox import InboxProcessorForPackages, InboxProcessorForBuilders, InboxItem, anti_ping_pong
from edge.generic import EdgeObject
from mongoengine.connection import get_db


def get_sighting_count(obs):
    sighting_count = getattr(obs, 'sighting_count', 1)
    if sighting_count is None:
        sighting_count = 1
    return sighting_count


def update_sighting_counts(additional_sightings, user):
    inbox_processor = InboxProcessorForBuilders(user=user)
    for id_, count in additional_sightings:
        edge_object = EdgeObject.load(id_)
        api_object = edge_object.to_ApiObject()
        api_object.obj.sighting_count = get_sighting_count(api_object.obs) + count
        inbox_processor.add(InboxItem(
            api_object=api_object,
            etlp=edge_object.etlp,
            etou=edge_object.etou,
            esms=edge_object.esms
        ))
    inbox_processor.run()


def existing_hash_dedup(contents, hashes, user):
    db = get_db()

    existing_items = db.stix.find({
        'created_by': user.id,
        'data.hash': {
            '$in': hashes.values()
        }
    }, {
        '_id': 1,
        'data.hash': 1
    })

    hash_to_existing_ids = {doc['data']['hash']: doc['_id'] for doc in existing_items}

    incoming_id_to_existing = {
        id_: hash_to_existing_ids[hash_] for id_, hash_ in hashes.iteritems() if hash_ in hash_to_existing_ids
    }

    out = {}
    additional_sightings = {}
    for id_, io in contents.iteritems():
        if id_ not in incoming_id_to_existing:
            io.api_object = io.api_object.remap(incoming_id_to_existing)
            out[id_] = io
        elif io.api_object.ty == 'obs':
            existing_id = incoming_id_to_existing[id_]
            sightings_for_duplicate = get_sighting_count(io.api_object.obj)
            additional_sightings[existing_id] = additional_sightings.get(existing_id, 0) + sightings_for_duplicate

    update_sighting_counts(additional_sightings, user)

    removed = len(contents) - len(out)
    message = ("Remapped %d objects to existing objects based on hashes" % removed) if removed else None

    return out, message


def new_hash_dedup(contents, hashes, user):
    return contents


class DedupInboxProcessor(InboxProcessorForPackages):
    filters = [
        anti_ping_pong,  # removes existing STIX objects matched by id
        existing_hash_dedup,  # removes existing STIX objects matched by hash
        new_hash_dedup  # removes new STIX objects matched by hash
    ]
