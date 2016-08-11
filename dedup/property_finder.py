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


def cve_finder(local):
    if local:
        namespace = LOCAL_NAMESPACE
    else:
        namespace = {'$ne': LOCAL_NAMESPACE}

    return get_db().stix.aggregate([
        {
            '$match': {
                'type': 'tgt',
                'data.idns': namespace,
                'data.api.vulnerabilities': {
                    '$exists': 'true'
                }
            }
        },
        {
            '$unwind': '$data.api.vulnerabilities'
        },
        {
            '$match': {
                'data.api.vulnerabilities.cve_id': {
                    '$exists': 'true'
                }
            }
        },
        {
            '$group': {
                '_id': '$_id',
                'cves': {
                    '$push': {
                        'cve': '$data.api.vulnerabilities.cve_id'
                    }
                }
            }
        },
        {
            '$sort': {'created_on': 1}
        }], cursor={})
