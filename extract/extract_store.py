import pymongo
from datetime import datetime
from mongoengine.connection import get_db

VALID_STATES = ["NEW", "PROCESSING", "FAILED", "COMPLETE"]


def _extract_store():
    return get_db().certuk_extracts


def create(user, filename, id):
    _extract_store().save({
        '_id': id,
        'timestamp': datetime.utcnow(),
        'user': user,
        'filename': filename,
        'state': "NEW",
        'message': '',
        'draft_ids': []
    })


def update(id, state, message, draft_ids):
    _extract_store().update(
        {'_id': id},
        { "$set": {'state': state if state in VALID_STATES else "COMPLETE",
         'message': message,
         'draft_ids': draft_ids} }
    )


def find(user=None, filename=None, state=None, limit=100):
    query = {}
    if user:
        query['user'] = {'$eq': user}
    if filename:
        query['filename'] = {'$eq': str(filename).upper()}
    if state and str(state).upper() in VALID_STATES:
        query['state'] = {'$eq': str(state).upper()}
    return [match for match in
            _extract_store()
                .find(query, {'_id': 0})
                .sort('timestamp', pymongo.DESCENDING)
                .limit(int(limit))]
