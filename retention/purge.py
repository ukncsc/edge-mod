
from mongoengine.connection import get_db
from edge import LOCAL_NAMESPACE
from datetime import datetime
from dateutil.relativedelta import relativedelta


class STIXPurge(object):

    def __init__(self, max_age_in_months, minimum_sightings, minimum_back_links):
        self.max_age_in_months = max_age_in_months
        self.minim_sightings = minimum_sightings
        self.minimum_back_links = minimum_back_links

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

        return list(old_external_ids)

    def run(self):
        pass
