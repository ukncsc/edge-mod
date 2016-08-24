import os
import subprocess

import repository.test as edge_test
from adapters.certuk_mod.backlinks.backlinks import STIXBacklinks
from mongoengine.connection import get_db

os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class BacklinkFunctionalTests(edge_test.TestCase):
    fixtures = ['stix']

    def loaddata(self, labels):
        for label in labels:
            pathname = os.path.dirname(__file__) + '/fixtures/' + label + '.json'
            subprocess.Popen(['mongoimport', '-d', edge_test.TEST_DB_NAME, '-c', label, '--file', pathname],
                             stdout=subprocess.PIPE).communicate()

    def test_simple(self):
        STIXBacklinks().run()
        db = get_db()
        self.assertEqual(db.stix_backlinks.count(), 3)
        self.assertEqual(db.stix_backlinks.find_one({"_id":"PurpleSecureSystems:observable-e4b88ebb-ea50-47df-9153-0e56a557d339"})['value']['PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515'], 'ind')
        self.assertEqual(db.stix_backlinks.find_one({"_id":"fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17"})['value']['PurpleSecureSystems:observable-e4b88ebb-ea50-47df-9153-0e56a557d339'], 'obs')
        self.assertIsNotNone(db.stix_backlinks.find_one({"_id":"max_created_on"}))


