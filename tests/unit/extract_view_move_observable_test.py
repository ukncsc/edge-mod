import unittest
import mock
import json
import copy
import hashlib
from adapters.certuk_mod.patch.indicator_patch import apply_patch
from adapters.certuk_mod.extract.views import extract_visualiser_move_observables, DRAFT_ID_SEPARATOR

apply_patch()

class DummyEo:
    def __init__(self, object):
        # type: (object) -> object
        self.init_object = object

    def to_draft(self):
        return self.init_object

class ExtractMoveTests(unittest.TestCase):
    def setUp(self):
        self.mock_request_patcher = mock.patch('django.http.request.HttpRequest')
        self.mock_extract_store_patcher = mock.patch('adapters.certuk_mod.extract.views.extract_store')
        self.mock_draft_upsert_patcher = mock.patch('users.models.Draft.upsert')
        self.mock_draft_load_patcher = mock.patch('users.models.Draft.load')
        self.mock_draft_delete_patcher = mock.patch('users.models.Draft.maybe_delete')

        self.mock_extract_store = self.mock_extract_store_patcher.start()
        self.mock_request = self.mock_request_patcher.start()
        self.mock_draft_upsert = self.mock_draft_upsert_patcher.start()
        self.mock_draft_load = self.mock_draft_load_patcher.start()
        self.mock_draft_delete = self.mock_draft_delete_patcher.start()

        self.init_stix_objects()

    def tearDown(self):
        self.mock_extract_store_patcher.stop()
        self.mock_request_patcher.stop()
        self.mock_draft_upsert_patcher.stop()
        self.mock_draft_load_patcher.stop()
        self.mock_draft_delete_patcher.stop()

    def init_stix_objects(self):
        obs0_title = 'test_draft_0'
        obs1_title = 'test_draft_1'

        self.draft_obs_id0 = 'observable:123' + DRAFT_ID_SEPARATOR + hashlib.md5(obs0_title.encode('utf-8')).hexdigest()
        self.draft_obs_id1 = 'observable:1234' + DRAFT_ID_SEPARATOR + hashlib.md5(obs1_title.encode('utf-8')).hexdigest()

        self.draft_obs0 = {'id': self.draft_obs_id0, 'title': obs0_title, 'objectType': 'File', 'file_name': "abc_draft.txt",
                           'hashes': []}
        self.draft_obs1 = {'id': self.draft_obs_id1, 'title': obs1_title, 'objectType': 'File', 'file_name': '',
                           'hashes': [{'hash_type': 'md5', 'hash_value': '123123123'}]}

        self.draft_ind_type = "typeA"
        self.draft_ind_id = 'indicator:123'
        self.draft_ind_title = 'hello'
        self.draft_ind_with_draft_obs = {'indicatorType': self.draft_ind_type, 'title': self.draft_ind_title,
                                         'id': self.draft_ind_id, 'observables': [self.draft_obs0, self.draft_obs1]}

        self.obs_id0 = 'observable:12345'
        self.obs0 = {'id': self.obs_id0, 'title': 'test0', 'objectType': 'File', 'file_name': "abc.txt", 'hashes':[]}

        self.draft_ind_with_mixed_obs_id = 'indicator:123'
        self.draft_ind_with_mixed_obs = {'indicatorType': self.draft_ind_type, 'title': self.draft_ind_title,
                                         'id': self.draft_ind_with_mixed_obs_id, 'observables': [self.draft_obs0, self.draft_obs1, self.obs0]}


    def test_move_draft_observable(self):
        self.mock_draft_load.side_effect = [copy.deepcopy(self.draft_ind_with_draft_obs),copy.deepcopy(self.draft_ind_with_draft_obs),copy.deepcopy(self.draft_ind_with_draft_obs)]
        self.mock_request.body = json.dumps({"id": self.draft_ind_id, "ids": [self.draft_obs_id0]})
        self.mock_extract_store.find.return_value = [{'_id':0, 'draft_ids': [self.draft_ind_id]}]
        extract_visualiser_move_observables(self.mock_request)

        self.assertEqual(self.mock_draft_upsert.call_args_list[0][0][1]['title'], self.draft_ind_title )
        self.assertEqual(self.mock_draft_upsert.call_args_list[0][0][1]['observables'], [self.draft_obs1])

        self.assertEqual(self.mock_draft_upsert.call_args_list[1][0][1]['title'], self.draft_ind_title+ '#1')
        self.assertEqual(self.mock_draft_upsert.call_args_list[1][0][1]['observables'], [self.draft_obs0])

    @mock.patch('adapters.certuk_mod.extract.extract_actions.EdgeObject')
    def test_move_existing_and_draft_observables(self, mock_EdgeObject):
        self.mock_draft_load.side_effect = [copy.deepcopy(self.draft_ind_with_mixed_obs),copy.deepcopy(self.draft_ind_with_mixed_obs),copy.deepcopy(self.draft_ind_with_mixed_obs)]
        self.mock_request.body = json.dumps({"id": self.draft_ind_id, "ids": [self.draft_obs_id0, self.obs_id0]})
        self.mock_extract_store.find.return_value = [{'_id':0, 'draft_ids': [self.draft_ind_with_mixed_obs_id]}]
        mock_EdgeObject.load.return_value = DummyEo(self.obs0)
        response = extract_visualiser_move_observables(self.mock_request)
        self.assertTrue(response.status_code == 200)
        self.assertEqual(self.mock_draft_upsert.call_args_list[0][0][1]['title'], self.draft_ind_title )
        self.assertEqual(self.mock_draft_upsert.call_args_list[0][0][1]['observables'], [self.draft_obs1])

        self.assertEqual(self.mock_draft_upsert.call_args_list[1][0][1]['title'], self.draft_ind_title+ '#1')
        newObservables = self.mock_draft_upsert.call_args_list[1][0][1]['observables']
        self.assertEqual(self.mock_draft_upsert.call_args_list[1][0][1]['observables'], [self.draft_obs0, self.obs0])