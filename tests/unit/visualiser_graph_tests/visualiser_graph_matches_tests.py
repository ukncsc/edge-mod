import unittest
import mock

from edge.generic import EdgeObject, EdgeReference
from adapters.certuk_mod.visualiser.graph import create_graph


class VisualiserGraphMatchesTests(unittest.TestCase):
    def setUp(self):
        self.mock_backlinks_exist_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.backlinks_exist')
        self.mock_matches_exist_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.matches_exist')
        self.mock_get_backlinks_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.get_backlinks')
        self.mock_get_matches_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.get_matches')

        self.mock_backlinks_exist = self.mock_backlinks_exist_patcher.start()
        self.mock_matches_exist = self.mock_matches_exist_patcher.start()
        self.mock_get_backlinks = self.mock_get_backlinks_patcher.start()
        self.mock_get_matches = self.mock_get_matches_patcher.start()

        self.init_stix_objects()

    def tearDown(self):
        self.mock_backlinks_exist_patcher.stop()
        self.mock_matches_exist_patcher.stop()
        self.mock_get_backlinks_patcher.stop()
        self.mock_get_matches_patcher.stop()

    def init_stix_objects(self):
        self.mock_edge_reference = mock.create_autospec(EdgeReference, id_='purple', ty='ind')
        self.mock_matching = mock.create_autospec(EdgeObject, id_='purple', summary={'title': ''}, ty='ind', edges=[])
        self.mock_matching2 = mock.create_autospec(EdgeObject, id_='orange', summary={'title': ''}, ty='coa',
                                               edges=[])

        self.matching_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': False,
                              'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': True,
                              'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.matching_node2 = {'id': 'orange', 'backlinks_shown': False, 'depth': 1, 'edges_shown': False,
                          'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': False,
                          'title': '',
                          'type': 'coa', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

    def test_create_graph_with_match_rel_type(self):
        id_matches = ['purple']
        stack = [(0, None, self.mock_matching, 'match')]
        response = create_graph(stack, [], id_matches, [], [])
        self.assertEquals(response['nodes'], [self.matching_node])
        self.assertEquals(response['links'], [])

    @mock.patch('adapters.certuk_mod.visualiser.graph.EdgeObject')
    def test_create_graph_with_match_link(self, mock_edge_object):
        id_matches = ['purple']
        self.mock_get_matches.return_value = ['matt']
        mock_edge_object.load.return_value = self.mock_matching2
        stack = [(0, None, self.mock_matching, 'match')]
        response = create_graph(stack, [], id_matches, [], [])
        links = [{'source': 0, 'target': 1, 'rel_type': 'match'}]
        self.assertEqual(response['nodes'][0], self.matching_node)
        self.assertEqual(response['nodes'][1], self.matching_node2)
        self.assertEqual(response['links'], links)

