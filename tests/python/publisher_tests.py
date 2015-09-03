
import unittest
import mock
import libtaxii
from package_publisher import Publisher


class PublisherTests(unittest.TestCase):

    @mock.patch('package_publisher.PublisherConfig', autospec=True)
    def test_PushPackage_IfNoSiteId_RaisesWarning(self, mock_config):
        configs = [{'site_id': None}, {}]
        for config in configs:
            with self.assertRaises(Warning):
                mock_config.get_config.return_value = config
                Publisher.push_package(None, None)

    @mock.patch('package_publisher.send_message')
    @mock.patch('package_publisher.discover_inbox_url')
    @mock.patch('package_publisher.PeerSite')
    @mock.patch('stix.core.stix_package.STIXPackage', autospec=True)
    @mock.patch('package_publisher.PublisherConfig', autospec=True)
    def test_PushPackage_IfSiteDetailsFound_SendsMessage(self, mock_config, mock_package, mock_peer_site,
                                                         mock_discover_inbox, mock_send_message):
        mock_config.get_config.return_value = {
            'site_id': 'Dummy site id',
            'namespace_id': 'Dummy namespace id',
            'namespace_alias': 'Dummy namespace alias'
        }
        mock_package.to_xml.return_value = ''
        mock_peer_site.objects.get.return_value = 'Dummy PeerSite'
        mock_discover_inbox.return_value = 'Dummy Inbox URL'

        Publisher.push_package(mock_package, {'namespace_id': '', 'namespace_alias': ''})

        send_message_call_args = mock_send_message.call_args[0]

        self.assertEqual(send_message_call_args[0], mock_peer_site.objects.get.return_value)
        self.assertEqual(send_message_call_args[1], mock_discover_inbox.return_value)
        self.assertIsInstance(send_message_call_args[2], libtaxii.tm11.InboxMessage)


if __name__ == '__main__':
    unittest.main()
