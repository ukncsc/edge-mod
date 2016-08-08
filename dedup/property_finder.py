from edge import LOCAL_NAMESPACE
from mongoengine.connection import get_db


def capec_finder(local, timestamp):
    match_query = {
        'type': 'ttp',
        'data.api.behavior.attack_patterns': {
            '$exists': 'true'
        }
    }
    if local:
        match_query.update({'data.idns': LOCAL_NAMESPACE})
    else:
        match_query.update({'data.idns': {'$ne': LOCAL_NAMESPACE}})

    if timestamp:
        match_query.update({'created_on': {'$lt': timestamp}})

    return get_db().stix.aggregate([
        {
            '$match': match_query
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


def cve_finder(local, timestamp):
    match_query = {
        'type': 'tgt',
        'data.api.vulnerabilities': {
            '$exists': 'true'
        }
    }
    if local:
        match_query.update({'data.idns': LOCAL_NAMESPACE})
    else:
        match_query.update({'data.idns': {'$ne': LOCAL_NAMESPACE}})

    if timestamp:
        match_query.update({'created_on': {'$lt': timestamp}})

    return get_db().stix.aggregate([
        {
            '$match': match_query
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
