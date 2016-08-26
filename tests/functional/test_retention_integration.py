import os
import subprocess
import mock
import repository.test as edge_test

from datetime import datetime
from adapters.certuk_mod.retention.purge import STIXPurge
from adapters.certuk_mod.retention.config import RetentionConfiguration
from mongoengine.connection import get_db

os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class RetentionFunctionalTests(edge_test.TestCase):
    fixtures = ['stix', 'schedules']

    def loaddata(self, labels):
        for label in labels:
            pathname = os.path.dirname(__file__) + '/retention/' + label + '.json'
            subprocess.Popen(['mongoimport', '-d', edge_test.TEST_DB_NAME, '-c', label, '--file', pathname],
                             stdout=subprocess.PIPE).communicate()

    @mock.patch('adapters.certuk_mod.retention.purge.LOCAL_NAMESPACE', 'http://www.purplesecure.com')
    @mock.patch('adapters.certuk_mod.retention.purge.datetime')
    def test_Purge_Local_NS(self, mock_datetime):
        stix_purge = STIXPurge(RetentionConfiguration.get())
        mock_datetime.utcnow.return_value = datetime(month=9, day=01, year=2016)

        self.assertEquals(
            get_db().stix.find({'_id': 'pss:observable-e2a95f85-1201-42b0-8b8b-6cabf8a933d7'}).count(), 1)
        self.assertEquals(get_db().stix.count(), 4)

        stix_purge.run()

        self.assertEquals(get_db().stix.count(), 3)
        self.assertEquals(get_db().stix.find_one({'_id': 'pss:observable-e2a95f85-1201-42b0-8b8b-6cabf8a933d7'}),
                          None)

    @mock.patch('adapters.certuk_mod.retention.purge.LOCAL_NAMESPACE', 'http://www.purplesecure.com')
    @mock.patch('adapters.certuk_mod.retention.purge.datetime')
    def test_Purge_External_NS(self, mock_datetime):
        mock_datetime.utcnow.return_value = datetime(month=9, day=01, year=2016)
        stix_purge = STIXPurge(RetentionConfiguration.set_from_dict({
            'max_age_in_months': 12,
            'minimum_sightings': 2,
            'minimum_back_links': 1,
            'localNamespaceOnly': False,
            'time': '00:00',
            'enabled': False
        }))

        self.assertEquals(
            get_db().stix.find({'_id': 'fireeye:observable-ed28d1a1-ab04-4f04-b7ae-78562a91286a'}).count(), 1)
        self.assertEquals(get_db().stix.count(), 4)

        stix_purge.run()

        self.assertEquals(get_db().stix.count(), 3)
        self.assertEquals(get_db().stix.find_one({'_id': 'fireeye:observable-ed28d1a1-ab04-4f04-b7ae-78562a91286a'}),
                          None)

    @mock.patch('adapters.certuk_mod.retention.purge.LOCAL_NAMESPACE', 'http://www.purplesecure.com')
    @mock.patch('adapters.certuk_mod.retention.purge.datetime')
    def test_Purge_Older_Local_NS(self, mock_datetime):
        mock_datetime.utcnow.return_value = datetime(month=9, day=01, year=2016)
        stix_purge = STIXPurge(RetentionConfiguration.set_from_dict({
            'max_age_in_months': 1,
            'minimum_sightings': 2,
            'minimum_back_links': 1,
            'localNamespaceOnly': True,
            'time': '00:00',
            'enabled': False
        }))

        self.assertEquals(
            get_db().stix.find({'_id': 'pss:observable-53dbd5cd-d76b-4703-b71c-b0ac6a629007'}).count(), 1)
        self.assertEquals(
            get_db().stix.find({'_id': 'pss:observable-e2a95f85-1201-42b0-8b8b-6cabf8a933d7'}).count(), 1)
        self.assertEquals(get_db().stix.count(), 4)

        stix_purge.run()

        self.assertEquals(get_db().stix.count(), 2)
        self.assertEquals(get_db().stix.find_one({'_id': 'pss:observable-53dbd5cd-d76b-4703-b71c-b0ac6a629007'}),
                          None)
        self.assertEquals(get_db().stix.find_one({'_id': 'pss:observable-e2a95f85-1201-42b0-8b8b-6cabf8a933d7'}),
                          None)

    @mock.patch('adapters.certuk_mod.retention.purge.LOCAL_NAMESPACE', 'http://www.purplesecure.com')
    @mock.patch('adapters.certuk_mod.retention.purge.datetime')
    def test_Purge_Older_External_NS(self, mock_datetime):
        mock_datetime.utcnow.return_value = datetime(month=9, day=01, year=2016)
        stix_purge = STIXPurge(RetentionConfiguration.set_from_dict({
            'max_age_in_months': 1,
            'minimum_sightings': 2,
            'minimum_back_links': 1,
            'localNamespaceOnly': False,
            'time': '00:00',
            'enabled': False
        }))

        self.assertEquals(
            get_db().stix.find({'_id': 'fireeye:observable-ed28d1a1-ab04-4f04-b7ae-78562a91286a'}).count(), 1)
        self.assertEquals(
            get_db().stix.find({'_id': 'fireeye:observable-18e9709d-2edd-455d-b62e-9cfb71c769e6'}).count(), 1)
        self.assertEquals(get_db().stix.count(), 4)

        stix_purge.run()

        self.assertEquals(get_db().stix.count(), 2)
        self.assertEquals(get_db().stix.find_one({'_id': 'fireeye:observable-ed28d1a1-ab04-4f04-b7ae-78562a91286a'}),
                          None)
        self.assertEquals(get_db().stix.find_one({'_id': 'fireeye:observable-18e9709d-2edd-455d-b62e-9cfb71c769e6'}),
                          None)
