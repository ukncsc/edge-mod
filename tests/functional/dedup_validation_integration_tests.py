import os
import io

import repository.test as edge_test
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from users.models import Repository_User
from edge.inbox import InboxError

os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class DedupFunctionalTests(edge_test.TestCase):
    def assert_load_file_ok(self, file_name):
        ip = self.create_inbox_from_file(file_name)
        ip.run()
        self.assertEqual(ip.message, 'Package Saved')

    def create_inbox_from_file(self, file_name):
        input_stream = io.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data',
                                            file_name))
        return DedupInboxProcessor(user=Repository_User(), streams=[(input_stream, None)])

    def assert_raises_inbox_error(self, file_name):
        ip = self.create_inbox_from_file(file_name)
        self.assertRaises(InboxError, ip.run)

    def test_DedupInboxProcessor_validate_IndicatorPackageWithTitleInHeaderNoChildTLP(self):
        self.assert_load_file_ok('IndicatorPackageWithTitleInHeaderNoChildTLP.xml')

    def test_DedupInboxProcessor_validate_IndicatorPackageWithNoTopLevelHandling(self):
        self.assert_load_file_ok('IndicatorPackageWithNoTopLevelHandling.xml')

    def test_DedupInboxProcessor_validate_IndicatorPackageWithNoHeader(self):
        self.assert_load_file_ok('IndicatorPackageWithNoHeader.xml')

    def test_DedupInboxProcessor_validate_IndicatorPackageWithNoTopLevelTLP(self):
        self.assert_load_file_ok('IndicatorPackageWithNoTopLevelTLP.xml')

    def test_DedupInboxProcessor_validate_IndicatorPackageWithRelatedPackage(self):
        self.assert_load_file_ok('IndicatorPackageWithRelatedPackage.xml')

    def test_DedupInboxProcessor_validate_IndicatorPackageWithNoTLPs(self):
        self.assert_raises_inbox_error('IndicatorPackageWithNoTLPs.xml')

    def test_DedupInboxProcessor_validate_IndicatorPackageNoTTPs(self):
        self.assert_raises_inbox_error('IndicatorPackageNoTTPs.xml')

    def test_DedupInboxProcessor_validate_correct_query(self):
        self.loaddata()

