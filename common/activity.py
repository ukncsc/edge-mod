import pymongo
from datetime import datetime
from mongoengine.connection import get_db

VALID_STATES = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]


def _activity_log():
    return get_db().certuk_activity


def save(user, category, state, message):
    _activity_log().save({
        'timestamp': datetime.utcnow(),
        'user': user,
        'category': category,
        'state': state if state in VALID_STATES else "INFO",
        'message': message
    })


def find(user=None, category=None, state=None, regex=None, limit=100):
    query = {}
    if user:
        query['user'] = {'$eq': user}
    if category:
        query['category'] = {'$eq': str(category).upper()}
    if state and str(state).upper() in VALID_STATES:
        query['state'] = {'$eq': str(state).upper()}
    if regex:
        query['message'] = {'$regex': regex, '$options': 'i'}
    return [match for match in
            _activity_log()
                .find(query, {'_id': 0})
                .sort('timestamp', pymongo.DESCENDING)
                .limit(int(limit))]
