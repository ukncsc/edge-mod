import unittest
import mock
from adapters.certuk_mod.extract.views import extract_visualiser_item_get


class ExtractTests(unittest.TestCase):
    @mock.patch('users.models.Draft.load')
    @mock.patch('users.models.Draft.list')
    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.extract.views.visualiser_item_get')
    def test_extract_visualiser_item_get_real_object(self, mock_visualiser_item_get, mock_request, mock_draft_list,
                                                     mock_draft_load):
        mock_draft_list.return_value = []
        mock_draft_load.return_value = {}
        mock_visualiser_item_get.return_value = None
        extract_visualiser_item_get(mock_request, '123')
        mock_visualiser_item_get.assert_called_with(mock_request, '123')

    @mock.patch('users.models.Draft.load')
    @mock.patch('users.models.Draft.list')
    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.extract.views.visualiser_item_get')
    def test_extract_visualiser_item_get_draft_indicator(self, mock_visualiser_item_get, mock_request, mock_draft_list,
                                                         mock_draft_load):
        id_ = '123'
        draft_ind = {'draft': {'id': id_}, 'observables': []}

        mock_draft_list.return_value = [draft_ind]
        mock_draft_load.return_value = draft_ind
        mock_visualiser_item_get.return_value = None

        class mock_json_response:
            def __init__(self, *args, **kwargs):
                self.content = args[0]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', mock_json_response):
            response = extract_visualiser_item_get(mock_request, id_)

        assert (response.content['root_id'] == id_)
        assert (response.content['validation_info'] == {})
        assert (response.content['package'] == {'indicators': [draft_ind]})
        mock_visualiser_item_get.assert_not_called()

    @mock.patch('users.models.Draft.load')
    @mock.patch('users.models.Draft.list')
    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.extract.views.visualiser_item_get')
    def test_extract_visualiser_item_get_draft_observable(self, mock_visualiser_item_get, mock_request, mock_draft_list,
                                                          mock_draft_load):
        id_ = 'indicator:123'
        id_obs0 = 'observable:123:draft:0'
        id_obs1 = 'observable:123:draft:1'
        draft_obs0 = {'id': id_obs0, 'title': 'test1', 'objectType': 'file'}
        draft_obs1 = {'id': id_obs1, 'title': 'test1', 'objectType': 'file'}
        draft_ind = {'draft': {'id': id_}, 'observables': [draft_obs0, draft_obs1]}

        mock_draft_list.return_value = [draft_ind]
        mock_draft_load.return_value = draft_ind
        mock_visualiser_item_get.return_value = None

        class mock_json_response:
            def __init__(self, *args, **kwargs):
                self.content = args[0]

        with mock.patch('adapters.certuk_mod.extract.views.JsonResponse', mock_json_response):
            response = extract_visualiser_item_get(mock_request, id_obs1)

        assert (response.content['root_id'] == id_obs1)
        assert (response.content['validation_info'] == {})
        assert (len(response.content['package']['observables']['observables']) == 1)
        mock_visualiser_item_get.assert_not_called()



