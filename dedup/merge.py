from mongoengine.connection import get_db
from mongoengine import DoesNotExist
from edge.generic import EdgeObject
from edge.models import StixBacklink


def merge_objects(raw_body):
    original, duplicate, type = raw_body['original'], raw_body['duplicate'], raw_body['type']
    map_table = {original: duplicate}
    existing_object = EdgeObject.load(original).to_ApiObject()
    existing_object.remap(map_table)

    parents_of_duplicate, parents_of_original = {}, {}
    try:
        parents_of_duplicate = StixBacklink.objects.get(id=duplicate).edges
    except DoesNotExist as e:
        pass
    try:
        parents_of_original = StixBacklink.objects.get(id=original).edges
    except DoesNotExist as e:
        pass
    new_parents = parents_of_duplicate.copy()
    new_parents.update(parents_of_original)
    update_original(original, duplicate, new_parents)


def update_original(original, duplicate, new_parents):
    get_db().stix_backlinks.update({'_id': original}, {'$set': {'value': new_parents}}, upsert=True)
    get_db().stix_backlinks.remove({'_id': duplicate})
    get_db().stix.remove({'_id': duplicate})
