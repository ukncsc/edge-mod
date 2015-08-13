
import unittest
import mock
from publisher_config import PublisherConfig


class PublisherConfigTests(unittest.TestCase):

    @mock.patch('publisher_config.PublisherConfig._unset_all_sites')
    def test_UpdateConfig_IfNoSiteId_UnsetAllSites(self, mock_unset_all_sites):
        new_configs = [
            {'site_id': None},
            {'site_id': ''}
        ]

        for new_config in new_configs:
            PublisherConfig.update_config(new_config)
            self.assertEqual(mock_unset_all_sites.call_count, 1)
            mock_unset_all_sites.reset_mock()

    @mock.patch('publisher_config.PublisherConfig._set_site')
    def test_UpdateConfig_IfSiteId_SetSite(self, mock_set_site):
        new_config = {'site_id': 'Dummy Site ID'}
        PublisherConfig.update_config(new_config)
        self.assertEqual(mock_set_site.call_count, 1)
        mock_set_site.assert_called_with(new_config['site_id'])

    @mock.patch('publisher_config.LOCAL_NAMESPACE', new='Dummy local namespace')
    @mock.patch('publisher_config.LOCAL_ALIAS', new='Dummy local alias')
    @mock.patch('publisher_config.get_db', autospec=True)
    def test_GetConfig_IfNoPublishSiteFound_ReturnNone(self, mock_db):
        mock_db.return_value.peer_sites.find_one.return_value = None
        config = PublisherConfig.get_config()
        self.assertIsNone(config['site_id'])

    @mock.patch('publisher_config.LOCAL_NAMESPACE', new='Dummy local namespace')
    @mock.patch('publisher_config.LOCAL_ALIAS', new='Dummy local alias')
    @mock.patch('publisher_config.get_db', autospec=True)
    def test_GetConfig_IfPublishSiteFound_ReturnSiteId(self, mock_db):
        dummy_site_id = 'Dummy Site ID'
        mock_db.return_value.peer_sites.find_one.return_value = {'_id': dummy_site_id}
        config = PublisherConfig.get_config()
        self.assertEqual(config['site_id'], dummy_site_id)


if __name__ == '__main__':
    unittest.main()
