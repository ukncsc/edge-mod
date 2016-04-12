import unittest
import mock
from adapters.certuk_mod.extract.views import extract_visualiser_get


class ExtractVisualiserTests(unittest.TestCase):

    def setUp(self):
        self.mock_valid_id_patcher = mock.patch('adapters.certuk_mod.extract.views.is_valid_stix_id')
        self.mock_request_patcher = mock.patch('django.http.request.HttpRequest')
        self.mock_draft_upsert_patcher = mock.patch('users.models.Draft.upsert')
        self.mock_draft_list_patcher = mock.patch('users.models.Draft.list')
        self.mock_draft_load_patcher = mock.patch('users.models.Draft.load')
        self.mock_db_patcher = mock.patch('adapters.certuk_mod.extract.views.get_db')
        self.mock_edge_load_patcher = mock.patch('edge.generic.EdgeObject.load')

        self.mock_valid_id = self.mock_valid_id_patcher.start()
        self.mock_valid_id.return_value = True

        self.mock_request = self.mock_request_patcher.start()
        self.mock_draft_upsert = self.mock_draft_upsert_patcher.start()
        self.mock_draft_list = self.mock_draft_list_patcher.start()
        self.mock_draft_load = self.mock_draft_load_patcher.start()
        self.mock_edge_load = self.mock_edge_load_patcher.start()
        self.mock_get_db = self.mock_db_patcher.start()
        self.init_stix_objects()

    def tearDown(self):
        self.mock_valid_id_patcher.stop()
        self.mock_request_patcher.stop()
        self.mock_draft_upsert_patcher.stop()
        self.mock_draft_list_patcher.stop()
        self.mock_draft_load_patcher.stop()
        self.mock_db_patcher.stop()
        self.mock_edge_load_patcher.stop()

    def init_stix_objects(self):
        self.ind_id_ = 'indicator:123'
        self.draft_id_obs0 = 'observable:123:draft:0'
        self.draft_id_obs1 = 'observable:123:draft:1'
        self.id_obs0 = 'observable:123'

        self.draft_obs0 = {'title': 'test0', 'objectType': 'File', 'filename': "abc.txt"}
        self.draft_obs1 = {'title': 'test1', 'objectType': 'File',
                            'hashes': [{'hash_type': 'md5', 'hash_value': '123123123'}]}

        self.obs0 = {'id':self.id_obs0, 'title': 'test1', 'objectType': 'File',
                      'hashes': [{'hash_type': 'md5', 'hash_value': '123123123'}]}

    class mockJsonResponse:
        def __init__(self, *args, **kwargs):
            self.content = args[0]

    def test_extract_visualiser_item_simple(self):

        draft_ind = {'id': self.ind_id_, 'observables': [self.draft_obs0, self.draft_obs1], 'title':""}

        self.mock_draft_load.return_value = draft_ind
        self.mock_draft_list.return_value = [draft_ind]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', self.mockJsonResponse):
            response = extract_visualiser_get(self.mock_request, self.ind_id_)

        self.assertEqual(len(response.content['nodes']), 3);
        self.assertEqual(len(response.content['links']), 2);

    def test_extract_visualiser_item_with_backlinks(self):
        mock_db_instance = mock.MagicMock()
        self.mock_get_db.return_value = mock_db_instance
        mock_db_instance.stix_backlinks.find = mock.MagicMock(return_value=[{'value': {'indicator:backlink':''}}])

        draft_ind = {'id': self.ind_id_, 'observables': [self.obs0, self.draft_obs1], 'title':""}
        obs_comp = mock.MagicMock()
        obs_comp.id = "obs_comp_id"
        obs_comp.obj.observable_composition.operator = 'Or'

        bl_ind = mock.MagicMock()
        bl_ind.id = "bl_ind_id"
        bl_ind.ty = "ind"

        self.mock_draft_load.return_value = draft_ind
        self.mock_edge_load.side_effect =  [obs_comp, bl_ind]
        self.mock_draft_list.return_value = [draft_ind]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', self.mockJsonResponse):
            response = extract_visualiser_get(self.mock_request, self.ind_id_)

        self.assertEqual(len(response.content['nodes']), 4);
        self.assertEqual(len(response.content['links']), 3);

    def test_extract_visualiser_item_with_backlinks_but_draft(self):
        mock_db_instance = mock.MagicMock()
        self.mock_get_db.return_value = mock_db_instance
        mock_db_instance.stix_backlinks.find = mock.MagicMock(return_value=[{'value': {'indicator:backlink':''}}])

        draft_ind = {'id': self.ind_id_, 'observables': [self.draft_obs0, self.draft_obs1], 'title':""}
        obs_comp = mock.MagicMock()
        obs_comp.id = "obs_comp_id"
        obs_comp.obj.observable_composition.operator = 'Or'

        bl_ind = mock.MagicMock()
        bl_ind.id = "bl_ind_id"
        bl_ind.ty = "ind"

        self.mock_draft_load.return_value = draft_ind
        self.mock_edge_load.side_effect =  [obs_comp, bl_ind]
        self.mock_draft_list.return_value = [draft_ind]

        class mock_json_response:
            def __init__(self, *args, **kwargs):
                self.content = args[0]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', mock_json_response):
            response = extract_visualiser_get(self.mock_request, self.ind_id_)

        self.assertEqual(len(response.content['nodes']), 3);
        self.assertEqual(len(response.content['links']), 2);
