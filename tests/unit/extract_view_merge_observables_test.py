import unittest
import mock
import hashlib
import json
from adapters.certuk_mod.extract.views import extract_visualiser_merge_observables, DRAFT_ID_SEPARATOR


class ExtractMergeTests(unittest.TestCase):

    def setUp(self):
        self.mock_valid_id_patcher = mock.patch('adapters.certuk_mod.extract.views.is_valid_stix_id')
        self.mock_request_patcher = mock.patch('django.http.request.HttpRequest')
        self.mock_draft_upsert_patcher = mock.patch('users.models.Draft.upsert')
        self.mock_draft_list_patcher = mock.patch('users.models.Draft.list')
        self.mock_draft_load_patcher = mock.patch('users.models.Draft.load')
        self.mock_draft_delete_patcher = mock.patch('users.models.Draft.maybe_delete')

        self.mock_valid_id = self.mock_valid_id_patcher.start()
        self.mock_valid_id.return_value = True

        self.mock_request = self.mock_request_patcher.start()
        self.mock_draft_upsert = self.mock_draft_upsert_patcher.start()
        self.mock_draft_list = self.mock_draft_list_patcher.start()
        self.mock_draft_load = self.mock_draft_load_patcher.start()
        self.mock_draft_delete = self.mock_draft_delete_patcher.start()
        self.init_stix_objects()

    def tearDown(self):
        self.mock_valid_id_patcher.stop()
        self.mock_request_patcher.stop()
        self.mock_draft_upsert_patcher.stop()
        self.mock_draft_list_patcher.stop()
        self.mock_draft_load_patcher.stop()
        self.mock_draft_delete_patcher.stop()

    def init_stix_objects(self):

        obs0_title = 'test0'
        obs1_title = 'test1'

        self.draft_obs_id0 = 'observable:123' + DRAFT_ID_SEPARATOR + hashlib.md5(obs0_title.encode('utf-8')).hexdigest()
        self.draft_obs_id1 = 'observable:123' + DRAFT_ID_SEPARATOR + hashlib.md5(obs1_title.encode('utf-8')).hexdigest()

        self.draft_obs0 = {'id': self.draft_obs_id0, 'title': obs0_title, 'objectType': 'File', 'file_name': "abc.txt", 'hashes':[]}
        self.draft_obs1 = {'id': self.draft_obs_id1, 'title': obs1_title, 'objectType': 'File', 'file_name':'',
                      'hashes': [{'hash_type': 'MD5', 'hash_value': '123123123'}]}

        self.draft_ind_id = 'indicator:123'
        self.draft_ind_with_draft_obs = {'id': self.draft_ind_id, 'observables': [self.draft_obs0, self.draft_obs1]}

        self.obs_id0 = 'observable:123'
        self.obs_id1 = 'observable:1234'
        self.obs0 = {'id': self.obs_id0, 'title': '', 'objectType': 'File', 'file_name': "abc.txt", 'hashes':[]}
        self.obs1 = {'id': self.obs_id1, 'title': '', 'objectType': 'File', 'file_name':'',
                      'hashes': [{'hash_type': 'MD5', 'hash_value': '123123123'}]}

        self.obs0_NotFile = {'id': self.obs_id0, 'title': 'test0', 'objectType': 'NotFile', 'file_name': "abc.txt", 'hashes':[]}

        self.draft_ind_with_obs = {'id': self.draft_ind_id, 'observables': [self.obs0, self.obs1]}

    def test_merge_observable(self):
        merged_obs = {'id': self.draft_obs_id0, 'title': 'abc.txt 123123123MD5', 'file_name': "abc.txt", 'objectType': 'File',
                      'hashes': [{'hash_type': 'MD5', 'hash_value': '123123123'}]}

        self.mock_draft_load.return_value = self.draft_ind_with_draft_obs
        self.mock_draft_list.return_value = [self.draft_ind_with_draft_obs]

        self.mock_request.body = json.dumps({"id": self.draft_ind_id, "ids": [self.draft_obs_id0, self.draft_obs_id1]})
        extract_visualiser_merge_observables(self.mock_request)
        self.mock_draft_upsert.assert_called_with('ind',
                                                  {'observables': [merged_obs],'id': 'indicator:123'},
                                                  self.mock_request.user)


    def test_try_merge_non_draft_observable(self):
        self.mock_draft_load.return_value = self.draft_ind_with_obs
        self.mock_draft_list.return_value = [self.draft_ind_with_obs]

        self.mock_request.body = json.dumps({"id":  self.draft_ind_id, "ids": [self.obs_id0]})
        response = extract_visualiser_merge_observables(self.mock_request)
        self.assertTrue(response.status_code == 400)
        self.mock_draft_upsert.assert_not_called()

    def test_try_merge_non_file_observable(self):

        draft_ind = {'draft': {'id': self.draft_ind_id}, 'observables': [self.obs0_NotFile, self.obs1]}

        self.mock_draft_load.return_value = draft_ind
        self.mock_draft_list.return_value = [draft_ind]

        self.mock_request.body = json.dumps({"id": self.draft_ind_id, "ids": [self.obs_id0]})
        extract_visualiser_merge_observables(self.mock_request)

        self.mock_draft_upsert.assert_not_called()
