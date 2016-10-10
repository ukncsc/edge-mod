import unittest
import mock
import json
import hashlib
from adapters.certuk_mod.extract.views import extract_visualiser_delete_observables, DRAFT_ID_SEPARATOR


class ExtractDeleteTests(unittest.TestCase):

    def setUp(self):
        self.mock_request_patcher = mock.patch('django.http.request.HttpRequest')
        self.mock_draft_upsert_patcher = mock.patch('users.models.Draft.upsert')
        self.mock_draft_load_patcher = mock.patch('users.models.Draft.load')
        self.mock_draft_delete_patcher = mock.patch('users.models.Draft.maybe_delete')

        self.mock_request = self.mock_request_patcher.start()
        self.mock_draft_upsert = self.mock_draft_upsert_patcher.start()
        self.mock_draft_load = self.mock_draft_load_patcher.start()
        self.mock_draft_delete = self.mock_draft_delete_patcher.start()

        self.init_stix_objects()

    def tearDown(self):
        self.mock_request_patcher.stop()
        self.mock_draft_upsert_patcher.stop()
        self.mock_draft_load_patcher.stop()
        self.mock_draft_delete_patcher.stop()

    def init_stix_objects(self):
        obs0_title = 'test0'
        obs1_title = 'test1'

        self.draft_obs_id0 = 'observable:123' + DRAFT_ID_SEPARATOR + hashlib.md5(obs0_title.encode('utf-8')).hexdigest()
        self.draft_obs_id1 = 'observable:123' + DRAFT_ID_SEPARATOR + hashlib.md5(obs1_title.encode('utf-8')).hexdigest()

        self.draft_obs0 = {'id': self.draft_obs_id0, 'title': obs0_title, 'objectType': 'File', 'file_name': "abc.txt", 'hashes':[]}
        self.draft_obs1 = {'id': self.draft_obs_id1, 'title': obs1_title, 'objectType': 'File', 'file_name':'',
                      'hashes': [{'hash_type': 'md5', 'hash_value': '123123123'}]}

        self.draft_ind_id = 'indicator:123'
        self.draft_ind_with_draft_obs = {'id': self.draft_ind_id, 'observables': [self.draft_obs0, self.draft_obs1]}

        self.obs_id0 = 'observable:123'
        self.obs_id1 = 'observable:1234'
        self.obs_id2 = 'observable:12345'
        self.obs0 = {'id': self.obs_id0, 'title': 'test0', 'objectType': 'File', 'file_name': "abc.txt", 'hashes':[]}
        self.obs1 = {'id': self.obs_id1, 'title': 'test1', 'objectType': 'File', 'file_name':'',
                      'hashes': [{'hash_type': 'md5', 'hash_value': '123123123'}]}

        self.obs0_NotFile = {'id': self.obs_id0, 'title': 'test0', 'objectType': 'NotFile', 'file_name': "abc.txt", 'hashes':[]}

        self.draft_ind_with_obs = {'id': self.draft_ind_id, 'observables': [self.obs0, self.obs1]}

    def test_delete_draft_observable(self):
        self.mock_draft_load.return_value = self.draft_ind_with_draft_obs
        self.mock_request.body = json.dumps({"id": self.draft_ind_id, "ids": [self.draft_obs_id0]})
        response = extract_visualiser_delete_observables(self.mock_request)
        self.assertTrue(response.status_code == 200)
        self.mock_draft_upsert.assert_called_with('ind', {'observables': [self.draft_obs1],
                                                     'id': self.draft_ind_id}, self.mock_request.user)
    def test_delete_existing_observable_with_draft_ind(self):
        self.mock_draft_load.return_value = self.draft_ind_with_obs
        self.mock_request.body = json.dumps({"id": self.draft_ind_id, "ids": [self.obs_id0]})
        response = extract_visualiser_delete_observables(self.mock_request)
        self.assertTrue(response.status_code == 200)
        self.mock_draft_upsert.assert_called_with('ind', {'observables': [self.obs1],
                                                          'id': self.draft_ind_id}, self.mock_request.user)
    def test_existing_observable_with_unrelated_draft_ind(self):
        self.mock_draft_load.return_value = self.draft_ind_with_obs
        self.mock_request.body = json.dumps({"id": self.draft_ind_id, "ids": [self.obs_id2]})
        response = extract_visualiser_delete_observables(self.mock_request)
        self.assertTrue(response.status_code == 400)
        self.mock_draft_upsert.assert_not_called()