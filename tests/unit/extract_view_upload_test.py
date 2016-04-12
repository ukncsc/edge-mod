import unittest
import mock
from adapters.certuk_mod.extract.views import extract_upload


class ExtractUploadTests(unittest.TestCase):
    @mock.patch('users.models.Draft.load')
    @mock.patch('users.models.Draft.upsert')
    @mock.patch('edge.generic.EdgeObject.load')
    @mock.patch('adapters.certuk_mod.extract.views.parse_file')
    @mock.patch('adapters.certuk_mod.extract.views.DedupInboxProcessor')
    @mock.patch('adapters.certuk_mod.extract.views.InboxProcessorForBuilders')
    @mock.patch('adapters.certuk_mod.extract.views.InboxItem')
    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.extract.views.redirect')
    def test_extract_upload_simple(self, mock_redirect, mock_request, mock_inbox_item, mock_builders_ip, mock_dedup_ip, mock_parse_file, mock_edge_load, mock_draft_upsert, mock_draft_load):
        mock_user = mock.MagicMock()
        mock_user.username = "user"
        mock_request.user = mock_user
        mock_indicator = mock.MagicMock()
        mock_indicator.api_object.ty = 'ind'
        mock_indicator.id = 'indicator1'

        mock_observable = {'id':"observable1"}
        mock_indicator.to_draft = mock.MagicMock(return_value={'id':'indicator1', 'observables':[mock_observable]})
        mock_dedup_instance = mock_dedup_ip.return_value
        mock_builders_ip_instance = mock_builders_ip.return_value
        mock_builders_ip_instance.add = mock.MagicMock()
        mock_dedup_instance.contents = {'indicator1': mock_indicator}
        mock_draft_load.return_value = mock_indicator

        mock_loaded_observable = mock.MagicMock()
        mock_loaded_observable.to_draft = mock.MagicMock(return_value={'id':'indicator1', 'observables':[mock_observable]})
        mock_edge_load.return_value = mock_loaded_observable

        extract_upload(mock_request)

        mock_draft_upsert.assert_called_with('ind', {'observables': [mock_observable], 'id': 'indicator1'}, mock_request.user)
        self.assertEqual(mock_builders_ip_instance.add.call_count, 1)
