import os
import subprocess
import repository.test as edge_test
import mock
import adapters.certuk_mod.tests.functional.online_dedup_tests.base_online_dedup_integration as online_dedup

from mongoengine.connection import get_db
os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class ObsCompOnlineDedupFunctionalTests(online_dedup.BaseOnlineDedupFunctionalTests):
    FILE_HASHES = {'MD5': "a01610228fe998f515a72dd730294d87",
                   'SHA224': '78d8045d684abd2eece923758f3cd781489df3a48e1278982466017f',
                   'SHA1': '356a192b7913b04c54574d18c28d46e6395428ab'}

    def loaddata(self, labels):
        for label in labels:
            pathname = os.path.dirname(__file__) + '/fixtures/' + label + '.json'
            subprocess.Popen(['mongoimport', '-d', edge_test.TEST_DB_NAME, '-c', label, '--file', pathname],
                             stdout=subprocess.PIPE).communicate()

    def get_file_hashes_for_file_obs(self, stix_id):
        file_hashes = [hashes for hashes in get_db().stix.find_one(stix_id)['data']['api']['object']['properties']['hashes']]
        return {hash['type']: hash['simple_hash_value'] for hash in file_hashes}

    # pss:observable-fa542208-6afb-4465-b0fa-e0f1cc8f5488 master
    # pss:observable-2db9432b-80dd-4e90-a98c-4a70036fe590 dup
    # Merge file hashes together => FILE_HASHES
    @mock.patch('adapters.certuk_mod.dedup.dedup.STIXDedup.LOCAL_ALIAS_REGEX', 'pss:')
    def test_OnlineDedup_validate_tlp_dedup(self):
        online_dedup = self.get_OnlineDedup_config()

        stix_count_before = self.get_Stix_Obj_Count({})
        in_edges_before = self.child_ID_in_Parent_Edges('pss:observable-fa542208-6afb-4465-b0fa-e0f1cc8f5488',
                                              'pss:observable-fa7590ac-fd4f-4a74-a84a-d0301f4ec667')
        in_backlinks_before = self.parent_ID_in_Childs_Backlinks('pss:observable-fa542208-6afb-4465-b0fa-e0f1cc8f5488',
                                              'pss:observable-fa7590ac-fd4f-4a74-a84a-d0301f4ec667')
        online_dedup.run()

        correct_obs_exists = self.get_Stix_Obj_Count({'_id': 'pss:observable-fa542208-6afb-4465-b0fa-e0f1cc8f5488'})
        deleted_obs_gone = self.get_Stix_Obj_Count({'_id': 'pss:observable-2db9432b-80dd-4e90-a98c-4a70036fe590'})

        stix_count_after = self.get_Stix_Obj_Count({})
        in_edges_after = self.child_ID_in_Parent_Edges('pss:observable-fa542208-6afb-4465-b0fa-e0f1cc8f5488',
                                              'pss:observable-fa7590ac-fd4f-4a74-a84a-d0301f4ec667')
        in_backlinks_after = self.parent_ID_in_Childs_Backlinks('pss:observable-fa542208-6afb-4465-b0fa-e0f1cc8f5488',
                                              'pss:observable-fa7590ac-fd4f-4a74-a84a-d0301f4ec667')


        self.assertEquals(1, stix_count_before - stix_count_after)
        self.assertEquals(1, correct_obs_exists)
        self.assertEquals(0, deleted_obs_gone)

        self.assertEquals(False, in_edges_before)
        self.assertEquals(True, in_edges_after)
        self.assertEquals(False, in_backlinks_before)
        self.assertEquals(True, in_backlinks_after)
        hashes_for_merged = self.get_file_hashes_for_file_obs({'_id': 'pss:observable-fa542208-6afb-4465-b0fa-e0f1cc8f5488'})
        self.assertDictEqual(hashes_for_merged, self.FILE_HASHES)

