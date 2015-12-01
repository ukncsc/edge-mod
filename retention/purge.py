
from mongoengine.connection import get_db
from edge import LOCAL_NAMESPACE
from datetime import datetime
from dateutil.relativedelta import relativedelta


class STIXPurge(object):

    def __init__(self, max_age_in_months, minimum_sightings):
        if not isinstance(max_age_in_months, int):
            raise TypeError('Integer required for max_age_in_months')
        if max_age_in_months < 0:
            raise ValueError('max_age_in_months must be greater than 0')
        self.max_age_in_months = max_age_in_months

        if not isinstance(minimum_sightings, int):
            raise TypeError('Integer required for minimum_sightings')
        if minimum_sightings < 2:
            raise ValueError('minimum_sightings must be greater than 1')
        self.minimum_sightings = minimum_sightings

    def _get_old_external_ids(self):
        current_date = datetime.utcnow()
        minimum_date = current_date - relativedelta(months=self.max_age_in_months)

        old_external_ids = get_db().stix.find({
            'created_on': {
                '$lt': minimum_date
            },
            'data.idns': {
                '$ne': LOCAL_NAMESPACE
            }
        }, {
            '_id': 1
        })
        old_external_ids = [doc['_id'] for doc in old_external_ids]

        return old_external_ids

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
                        '$lt': self.minimum_sightings
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
        if (self.minimum_sightings - 1) > 1:
            query.update({
                '_id': {
                    '$in': ids_old_ext_no_back_links
                },
            })

        ids_to_delete = get_db().stix.find(query, {
            '_id': 1
        })

        return ids_to_delete

    def get_purge_candidates(self):
        old_external_ids = self._get_old_external_ids()

        if not old_external_ids:
            return None

        items_no_back_links = self._get_items_with_no_back_links(old_external_ids)

        if not items_no_back_links:
            return None

        hashes_deletion_candidates = self._get_hashes_for_possible_deletion(items_no_back_links.values())

        ids_to_delete = self._get_ids_for_deletion(hashes_deletion_candidates, items_no_back_links.keys())

        return ids_to_delete

    def run(self):
        ids_to_delete = self.get_purge_candidates()
        if ids_to_delete:
            get_db().stix.remove({
                '_id': {
                    '$in': list(ids_to_delete)
                }
            })
