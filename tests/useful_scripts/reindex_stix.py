from mongoengine.connection import get_db

from pymongo import MongoClient

client = MongoClient()
db = client.inbox

# full-text-search index
db.stix.ensure_index(
        [('fts', 'text')],
        name='idx_fts',
        background=True,
    )


# create default indexes
db.stix.ensure_index([('data.hash',1)])
db.stix.ensure_index([('type',1)])
db.stix.ensure_index([('created_on',1)])

db.stix.ensure_index([('data.summary.type', 1)])
db.stix.ensure_index([('txn',1)])
db.stix.ensure_index([('data.summary.title', 1)])

db.activity.log.ensure_index([('stix_id', 1)])

# cache index and uniqueness
db.cache.ensure_index([('cache_name', 1)])

# unique index on name
db.trust_group.ensure_index([('name', 1)], unique=True)
