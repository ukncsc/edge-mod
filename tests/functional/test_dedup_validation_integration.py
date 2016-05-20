import os
import io
import subprocess

import repository.test as edge_test
from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from users.models import Repository_User
from edge.inbox import InboxError

os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class DedupFunctionalTests(edge_test.TestCase):

    fixtures = ['stix']

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

    def loaddata(self, labels):
         for label in labels:
            pathname = os.path.dirname(__file__) + '/ttps/' + label + '.json'
            subprocess.Popen(['mongoimport', '-d', edge_test.TEST_DB_NAME, '-c', label, '--file', pathname],
                             stdout=subprocess.PIPE).communicate()

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

    def test_DedupInboxProcessor_validate_correct_ttp_dedup_message_remapping(self):
        ip = self.create_inbox_from_file('TTP-PackageWithRemapping.xml')
        ip.run()
        remap = 'Remapped 11 local namespace TTPs to existing TTPs based on CAPEC-IDs and title'
        self.assertEqual(ip.filter_messages[1], remap)

    def test_DedupInboxProcessor_validate_correct_ttp_dedup_message_merge_and_remapping(self):
        ip = self.create_inbox_from_file('TTP-PackageWithMergeAndRemapping.xml')
        ip.run()
        merge = 'Merged 2 local namespace TTPs in the supplied package based on CAPEC-IDs and title'
        remap = 'Remapped 6 local namespace TTPs to existing TTPs based on CAPEC-IDs and title'
        self.assertEqual(ip.filter_messages[1], merge)
        self.assertEqual(ip.filter_messages[2], remap)

    def test_DedupInboxProcessor_validate_correct_ttp_dedup_message_merge(self):
        ip = self.create_inbox_from_file('TTP-PackageWithMerge.xml')
        ip.run()
        merge = 'Merged 3 local namespace TTPs in the supplied package based on CAPEC-IDs and title'
        self.assertEqual(ip.filter_messages[1], merge)

    def test_DedupInboxProcessor_validate_correct_tgt_dedup_message_merge(self):
        ip = self.create_inbox_from_file('TGT-PackageWithMerge.xml')
        ip.run()
        merge = 'Merged 2 local namespace Exploit Targets in the supplied package based on CVE-IDs'
        self.assertEqual(ip.filter_messages[1], merge)

    def test_DedupInboxProcessor_validate_correct_tgt_dedup_message_remapping(self):
        ip = self.create_inbox_from_file('TGT-PackageWithRemapping.xml')
        ip.run()
        remap = 'Remapped 2 local namespace Exploit Targets to existing Targets based on CVE-IDs'
        self.assertEqual(ip.filter_messages[1], remap)

    def test_DedupInboxProcessor_validate_correct_tgt_dedup_message_merge_and_remapping(self):
        ip = self.create_inbox_from_file('TGT-PackageWithMergeAndRemapping.xml')
        ip.run()
        merge = 'Merged 5 local namespace Exploit Targets in the supplied package based on CVE-IDs'
        remap = 'Remapped 2 local namespace Exploit Targets to existing Targets based on CVE-IDs'
        self.assertEqual(ip.filter_messages[1], merge)
        self.assertEqual(ip.filter_messages[2], remap)

