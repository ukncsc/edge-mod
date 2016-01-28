import unittest
import mock

from cybox.core import Observable
from edge.generic import ApiObject, EdgeObject
from edge.inbox import InboxError

from users.models import Repository_User

from adapters.certuk_mod.dedup.DedupInboxProcessor import get_sighting_count, update_sighting_counts


class DedupInboxProcessorTests(unittest.TestCase):
    def test_get_sighting_count_not_set(self):
        obs = Observable()
        actual = get_sighting_count(obs)
        self.assertEqual(actual, 1)

    def test_get_sighting_count_set_to_none(self):
        obs = Observable()
        obs.sighting_count = None
        actual = get_sighting_count(obs)
        self.assertEqual(actual, 1)

    def test_get_sighting_count_set_to_one(self):
        obs = Observable()
        obs.sighting_count = 1
        actual = get_sighting_count(obs)
        self.assertEqual(actual, 1)

    def test_get_sighting_count_set_to_two(self):
        obs = Observable()
        obs.sighting_count = 2
        actual = get_sighting_count(obs)
        self.assertEqual(actual, 2)

    def test_update_sighting_counts_no_additional_sightings(self):
        self.assertRaises(InboxError, update_sighting_counts, dict(),
                          mock.Mock(name='username', spec_set=Repository_User))

    @mock.patch('edge.inbox.InboxItem')
    @mock.patch.object(EdgeObject, 'load')
    @mock.patch('edge.inbox.InboxProcessorForBuilders')
    def test_update_sighting_counts_one_additional_sighting(self, mock_inbox_processor, mock_edge_object, mock_inbox_item):
        mock_edge_object = EdgeObject({
            '_id': 'an-id',
            'type': 'obs',
            'data': {
                'api': {

                },
                'idns': 'ns',
                'etlp': 'WHITE',
                'summary': 'Summary',
                'hash': 'hash',
            },
            'cv': 0,
            'tg': None
        })
        update_sighting_counts({'an-id': 1}, mock.Mock(name='username', spec_set=Repository_User))
