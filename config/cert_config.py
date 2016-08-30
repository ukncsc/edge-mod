from mongoengine.connection import get_db


def _config():
    return get_db().certuk_config


def save(name, value):
    _config().update({
        'name': name
    }, {
        '$setOnInsert': {
            'name': name,
        },
        '$set': {
            'value': value
        }
    }, True)


def get(name):
    value = _config().find_one({
        'name': name
    })

    if value is not None:
        return value.get('value')
    else:
        return value


def get_all():
    cursor = _config().find({}, {
        '_id': 0
    })
    results = {}
    for doc in cursor:
        results[doc["name"]] = doc["value"]

    return results
