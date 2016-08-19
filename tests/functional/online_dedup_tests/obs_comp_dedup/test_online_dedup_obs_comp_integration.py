import os
import subprocess
import repository.test as edge_test
import mock
import adapters.certuk_mod.tests.functional.online_dedup_tests.base_online_dedup_integration as online_dedup

from mongoengine.connection import get_db
os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class ObsCompOnlineDedupFunctionalTests(online_dedup.BaseOnlineDedupFunctionalTests):

    def loaddata(self, labels):
        for label in labels:
            pathname = os.path.dirname(__file__) + '/fixtures/' + label + '.json'
            subprocess.Popen(['mongoimport', '-d', edge_test.TEST_DB_NAME, '-c', label, '--file', pathname],
                             stdout=subprocess.PIPE).communicate()

    def test_Obs_Comp_not_Deduped(self):
        self.OnlineDedup_validate_nothing_deduped()
