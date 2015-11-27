
from mongoengine.connection import get_db
from bson import Code
from edge import LOCAL_NAMESPACE
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os


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

    @staticmethod
    def __get_sightings_map_function():
        with open(os.path.join(os.path.dirname(__file__), 'sightings-map.js')) as _file:
            return _file.read().replace('sightingsMap', '')

    @staticmethod
    def __get_sightings_reduce_function():
        with open(os.path.join(os.path.dirname(__file__), 'sightings-reduce.js')) as _file:
            return _file.read().replace('sightingsReduce', '')

    def get_purge_candidates(self):
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

        if len(old_external_ids) == 0:
            return None

        old_with_back_link_ids = get_db().stix_backlinks.find({
            '_id': {
                '$in': old_external_ids
            }
        }, {
            '_id': 1
        })
        old_with_back_link_ids = [doc['_id'] for doc in old_with_back_link_ids]

        if len(old_external_ids) == len(old_with_back_link_ids):
            return None

        old_with_no_back_link_ids = list(set(old_external_ids) - set(old_with_back_link_ids))

        hash_counts = get_db().stix.map_reduce(Code(self.__get_sightings_map_function()),
                                               Code(self.__get_sightings_reduce_function()),
                                               out={
                                                   'inline': 1
                                               })

        hashes = [doc['_id'] for doc in hash_counts['results'] if doc['value'] < self.minimum_sightings]

        ids_to_delete = get_db().stix.find({
            '_id': {
                '$in': old_with_no_back_link_ids
            },
            'data.hash': {
                '$in': hashes
            }
        }, {
            '_id': 1
        })

        return ids_to_delete

    def run(self):
        ids_to_delete = self.get_purge_candidates()
        if ids_to_delete:
            get_db().stix.remove({
                '_id': {
                    '$in': list(ids_to_delete)
                }
            })
