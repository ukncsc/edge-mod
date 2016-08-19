from mongoengine.connection import get_db


class DuplicateFinder(object):

    @staticmethod
    def find_duplicates(edge_object):
        duplicates = [doc['_id'] for doc in get_db().stix.find({
            'data.hash': edge_object.doc['data']['hash'],
            'type': edge_object.ty,
            '_id': {'$ne': edge_object.id_}
        }, {'_id': 1})]

        return duplicates
