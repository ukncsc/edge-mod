# -*- coding: utf-8 -*-
import unittest
import mock
import hashlib
from adapters.certuk_mod.extract.views import extract_visualiser_item_get


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.mock_request_patcher = mock.patch('django.http.request.HttpRequest')
        self.mock_draft_list_patcher = mock.patch('users.models.Draft.list')
        self.mock_draft_load_patcher = mock.patch('users.models.Draft.load')
        self.mock_get_item_patcher = mock.patch('adapters.certuk_mod.extract.views.visualiser_item_get')

        self.mock_request = self.mock_request_patcher.start()
        self.mock_get_item = self.mock_get_item_patcher.start()
        self.mock_get_item.return_value = None
        self.mock_draft_list = self.mock_draft_list_patcher.start()
        self.mock_draft_load = self.mock_draft_load_patcher.start()

    def tearDown(self):
        self.mock_request_patcher.stop()
        self.mock_draft_list_patcher.stop()
        self.mock_draft_load_patcher.stop()
        self.mock_get_item_patcher.stop()

    def test_extract_visualiser_item_get_real_object(self):
        self.mock_draft_list.return_value = []
        self.mock_draft_load.return_value = {}
        extract_visualiser_item_get(self.mock_request, '123')
        self.mock_get_item.assert_called_with(self.mock_request, '123')

    def test_extract_visualiser_item_get_draft_indicator(self):
        id_ = '123'
        draft_ind = {'draft': {'id': id_}, 'observables': []}

        self.mock_draft_list.return_value = [draft_ind]
        self.mock_draft_load.return_value = draft_ind

        class mockJsonResponse:
            def __init__(self, *args, **kwargs):
                self.content = args[0]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', mockJsonResponse):
            response = extract_visualiser_item_get(self.mock_request, id_)

        assert (response.content['root_id'] == id_)
        assert (response.content['validation_info'] == {})
        assert (response.content['package'] == {'indicators': [draft_ind]})
        self.mock_get_item.assert_not_called()

    def test_extract_visualiser_item_get_draft_observable(self):
        id_ = 'indicator:123'

        obs0_title = 'test0'
        obs1_title = 'test1'

        id_obs0 = 'observable:123:draft:' + hashlib.md5(obs0_title.encode('utf-8')).hexdigest()
        id_obs1 = 'observable:123:draft:' + hashlib.md5(obs1_title.encode('utf-8')).hexdigest()

        draft_obs0 = {'id': id_obs0, 'title': obs0_title, 'objectType': 'file'}
        draft_obs1 = {'id': id_obs1, 'title': obs1_title, 'objectType': 'file'}
        draft_ind = {'draft': {'id': id_}, 'observables': [draft_obs0, draft_obs1]}

        self.mock_draft_list.return_value = [draft_ind]
        self.mock_draft_load.return_value = draft_ind

        class mockJsonResponse:
            def __init__(self, *args, **kwargs):
                self.content = args[0]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', mockJsonResponse):
            response = extract_visualiser_item_get(self.mock_request, id_obs1)

        assert (response.content['root_id'] == id_obs1)
        assert (response.content['validation_info'] == {})
        assert (len(response.content['package']['observables']['observables']) == 1)
        self.mock_get_item.assert_not_called()


    def test_extract_visualiser_item_get_draft_observable_unicode(self):
        id_ = 'indicator:123'

        obs0_title = u'ééé'
        obs1_title = 'test1'

        id_obs0 = 'observable:123:draft:' + hashlib.md5(obs0_title.encode('utf-8')).hexdigest()
        id_obs1 = 'observable:123:draft:' + hashlib.md5(obs1_title.encode('utf-8')).hexdigest()

        draft_obs0 = {'id': id_obs0, 'title':u'ééé' , 'objectType': 'file', 'value':123}
        draft_obs1 = {'id': id_obs1, 'title': 'test1', 'objectType': 'file', 'value':456}
        draft_ind = {'draft': {'id': id_}, 'observables': [draft_obs0, draft_obs1]}

        self.mock_draft_list.return_value = [draft_ind]
        self.mock_draft_load.return_value = draft_ind

        class mockJsonResponse:
            def __init__(self, *args, **kwargs):
                self.content = args[0]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', mockJsonResponse):
            response = extract_visualiser_item_get(self.mock_request, id_obs0)

        assert (response.content['root_id'] == id_obs0)
        assert (response.content['validation_info'] == {})
        assert (len(response.content['package']['observables']['observables']) == 1)
        assert (response.content['package']['observables']['observables'][0]['object']['properties']['value'] == u'file:ééé')
        self.mock_get_item.assert_not_called()
