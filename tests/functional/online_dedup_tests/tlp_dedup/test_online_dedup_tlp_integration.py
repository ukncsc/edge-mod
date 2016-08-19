import os
import subprocess
import repository.test as edge_test
import mock
import adapters.certuk_mod.tests.functional.online_dedup_tests.base_online_dedup_integration as online_dedup

os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class TLPOnlineDedupFunctionalTests(online_dedup.BaseOnlineDedupFunctionalTests):

    def loaddata(self, labels):
        for label in labels:
            pathname = os.path.dirname(__file__) + '/fixtures/' + label + '.json'
            subprocess.Popen(['mongoimport', '-d', edge_test.TEST_DB_NAME, '-c', label, '--file', pathname],
                             stdout=subprocess.PIPE).communicate()

    # fireeye:observable-c7d7c4a3-8dd6-4e0a-9023-dd5a248cfb66. TLP = WHITE
    # fireeye:observable-ed28d1a1-ab04-4f04-b7ae-78562a91286a. TLP = RED
    # => dedup to TLP WHITE
    @mock.patch('adapters.certuk_mod.dedup.dedup.STIXDedup.LOCAL_ALIAS_REGEX', 'pss:')
    def test_OnlineDedup_validate_tlp_dedup(self):
        online_dedup = self.get_OnlineDedup_config()

        stix_count_before = self.get_Stix_Obj_Count({})
        in_edges_before = self.child_ID_in_Parent_Edges('fireeye:observable-c7d7c4a3-8dd6-4e0a-9023-dd5a248cfb66',
                                              'fireeye:indicator-c7d7853e-440e-4bc9-8527-1ba677b264af')
        in_backlinks_before = self.parent_ID_in_Childs_Backlinks('fireeye:observable-c7d7c4a3-8dd6-4e0a-9023-dd5a248cfb66',
                                              'fireeye:indicator-c7d7853e-440e-4bc9-8527-1ba677b264af')
        online_dedup.run()

        correct_obs_exists = self.get_Stix_Obj_Count({'_id': 'fireeye:observable-c7d7c4a3-8dd6-4e0a-9023-dd5a248cfb66'})
        deleted_obs_gone = self.get_Stix_Obj_Count({'_id': 'fireeye:observable-ed28d1a1-ab04-4f04-b7ae-78562a91286a'})

        stix_count_after = self.get_Stix_Obj_Count({})
        in_edges_after = self.child_ID_in_Parent_Edges('fireeye:observable-c7d7c4a3-8dd6-4e0a-9023-dd5a248cfb66',
                                              'fireeye:indicator-c7d7853e-440e-4bc9-8527-1ba677b264af')
        in_backlinks_after = self.parent_ID_in_Childs_Backlinks('fireeye:observable-c7d7c4a3-8dd6-4e0a-9023-dd5a248cfb66',
                                              'fireeye:indicator-c7d7853e-440e-4bc9-8527-1ba677b264af')

        self.assertEquals(1, stix_count_before - stix_count_after)
        self.assertEquals(1, correct_obs_exists)
        self.assertEquals(0, deleted_obs_gone)

        self.assertEquals(False, in_edges_before)
        self.assertEquals(True, in_edges_after)
        self.assertEquals(False, in_backlinks_before)
        self.assertEquals(True, in_backlinks_after)
