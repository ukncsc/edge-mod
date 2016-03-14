from mongoengine.connection import get_db

def _config():
    return get_db().certuk_config


def save(field, value):
    if validate(value):
        _config().save({
            field: value
        })


def get(field):
    return _config().findOne({
        field: {
            "$exists" : "true"
        }
    });


def validate(value):
    return True;
