from edge import LOCAL_NAMESPACE
from mongoengine.connection import get_db

def capec_finder(local):
    if local:
        namespace = LOCAL_NAMESPACE
    else:
        namespace = {'$ne': LOCAL_NAMESPACE}
    return get_db().stix.aggregate([
        {
            '$match': {
                'type': 'ttp',
                'data.idns': namespace,
                'data.api.behavior.attack_patterns': {
                    '$exists': 'true'
                }
            }
        },
        {
            '$unwind': '$data.api.behavior.attack_patterns'
        },
        {
            '$match': {
                'data.api.behavior.attack_patterns.capec_id': {
                    '$exists': 'true'
                }
            }
        },
        {
            '$group': {
                '_id': '$_id',
                'capecs': {
                    '$push': {
                        'capec': '$data.api.behavior.attack_patterns.capec_id'
                    }
                },
                'title': {
                    '$first': '$data.api.title'
                }
            }
        }, {
            '$sort': {'created_on': 1}
        }], cursor={})
