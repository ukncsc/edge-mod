
from mongoengine.connection import get_db
from edge import LOCAL_NAMESPACE
from datetime import datetime
from dateutil.relativedelta import relativedelta


class STIXPurge(object):

    PAGE_SIZE = 10000

    def __init__(self, retention_config):
        self.retention_config = retention_config

    def _get_old_external_ids(self, minimum_date, version_epoch):
        old_external_ids = get_db().stix.find({
            'created_on': {
                '$lt': minimum_date
            },
            'data.idns': {
                '$ne': LOCAL_NAMESPACE
            },
            'cv': {
                '$lte': str(version_epoch)
            }
        }, {
            '_id': 1,
            'created_on': 1
        }).sort('created_on', -1).limit(self.PAGE_SIZE)

        old_external_ids = list(old_external_ids)
        if not old_external_ids:
            return None, []
        new_minimum_date = old_external_ids[-1]['created_on']

        old_external_ids = [doc['_id'] for doc in old_external_ids]

        return new_minimum_date, old_external_ids

    @staticmethod
    def _get_items_with_no_back_links(ids_to_search):
        with_back_link_ids = get_db().stix_backlinks.find({
            '_id': {
                '$in': ids_to_search
            }
        }, {
            '_id': 1
            # stix_backlinks doesn't contain the hash unfortunately...
        })
        with_back_link_ids = [doc['_id'] for doc in with_back_link_ids]

        if len(ids_to_search) == len(with_back_link_ids):
            return {}

        no_back_link_ids = list(set(ids_to_search) - set(with_back_link_ids))

        no_back_links_objects = get_db().stix.find({
            '_id': {
                '$in': no_back_link_ids
            }
        }, {
            '_id': 1,
            'data.hash': 1
        })
        no_back_links_objects = {doc['_id']: doc['data']['hash'] for doc in no_back_links_objects}

        return no_back_links_objects

    def _get_hashes_for_possible_deletion(self, qualifying_hashes):
        hash_counts = get_db().stix.aggregate([
            {
                '$match': {
                    'data.hash': {
                        '$in': qualifying_hashes
                    }
                }
            },
            {
                '$group': {
                    '_id': '$data.hash',
                    'sightings': {
                        '$sum': {
                            '$cond': [
                                '$data.api.sightings_count',
                                '$data.api.sightings_count',
                                1
                            ]
                        }
                    }
                }
            },
            {
                '$match': {
                    'sightings': {
                        '$lt': self.retention_config.minimum_sightings
                    }
                }
            }
        ], cursor={})

        hashes = [doc['_id'] for doc in hash_counts]

        return hashes

    def _get_ids_for_deletion(self, hashes_lt_min_sightings, ids_old_ext_no_back_links):
        query = {
            'data.hash': {
                '$in': hashes_lt_min_sightings
            }
        }
        # If we are deleting things with more than 1 hash-based sighting, then we must filter by id too, otherwise we
        #  risk deleting items that are from our namespace/have back links/aren't old etc...
        if (self.retention_config.minimum_sightings - 1) > 1:
            query.update({
                '_id': {
                    '$in': ids_old_ext_no_back_links
                },
            })

        ids_to_delete = get_db().stix.find(query, {
            '_id': 1
        })

        return [doc['_id'] for doc in ids_to_delete]

    def get_purge_candidates(self):
        current_date = datetime.utcnow()
        minimum_date = current_date - relativedelta(months=self.retention_config.max_age_in_months)
        version_epoch = int(1000* (minimum_date - datetime(1970, 1, 1)).total_seconds() + 0.5)

        ids_to_delete = []
        while True:
            minimum_date, old_external_ids = self._get_old_external_ids(minimum_date, version_epoch)

            if not old_external_ids:
                break

            items_no_back_links = self._get_items_with_no_back_links(old_external_ids)

            if not items_no_back_links:
                continue

            hashes_deletion_candidates = self._get_hashes_for_possible_deletion(items_no_back_links.values())

            ids_to_delete += self._get_ids_for_deletion(hashes_deletion_candidates, items_no_back_links.keys())

        return ids_to_delete

    def run(self):
        ids_to_delete = self.get_purge_candidates()
        if ids_to_delete:
            for page_index in range(0, len(ids_to_delete), self.PAGE_SIZE):
                chunk_ids = ids_to_delete[page_index: page_index + self.PAGE_SIZE]
                if chunk_ids:
                    get_db().stix.remove({
                        '_id': {
                            '$in': chunk_ids
                        }
                    })
