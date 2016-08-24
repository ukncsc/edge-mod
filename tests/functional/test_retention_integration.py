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
    fixtures = ['stix', 'schedules', 'stix_backlinks']

    def loaddata(self, labels):
        for label in labels:
            pathname = os.path.dirname(__file__) + '/retention/' + label + '.json'
            subprocess.Popen(['mongoimport', '-d', edge_test.TEST_DB_NAME, '-c', label, '--file', pathname],
                             stdout=subprocess.PIPE).communicate()

    @mock.patch('adapters.certuk_mod.retention.purge.LOCAL_NAMESPACE', 'http://www.purplesecure.com')
    @mock.patch('adapters.certuk_mod.retention.purge.datetime')
    def test_Purge_Local_NS(self, mock_datetime):
        mock_datetime.utc.return_value = datetime(month=9, day=01, year=2016)
        stix_purge = STIXPurge(RetentionConfiguration.get())
        self.assertEquals(get_db().stix.count(), 4)

