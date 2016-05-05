import os
from mongoengine import connection, connect
PAGE_SIZE = 5000

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')


def run():

    connect("inbox", host="127.0.0.1", port=27017)
    db = connection.get_db()

    bulk_op = db.stix.initialize_unordered_bulk_op()
    update_count = 0
    for doc in db.stix.find():
        fts_data = {'fts': None}

        update_count += 1
        bulk_op.find({'_id': doc['_id']}).update({'$set': fts_data})
        if not update_count % PAGE_SIZE:
            bulk_op.execute()
            bulk_op = db.stix.initialize_unordered_bulk_op()

    if update_count % PAGE_SIZE:
        bulk_op.execute()

if __name__ == '__main__':
    run()

