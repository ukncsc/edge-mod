import mock
import unittest

from adapters.certuk_mod.visualiser.graph import get_backlinks, get_matches, backlinks_exist, matches_exist, \
    create_graph

from edge.generic import EdgeObject, EdgeReference


class VisualiserGraphTests(unittest.TestCase):

    @mock.patch('adapters.certuk_mod.visualiser.graph.get_matches')
    def test_matches_do_exist(self, mock_matches):
        mock_matches.return_value = []
        matches = matches_exist('')
        mock_matches.assert_called_with('')
        self.assertEquals(matches, False)

    @mock.patch('adapters.certuk_mod.visualiser.graph.get_matches')
    def test_matches_do_not_exist(self, mock_matches):
        mock_matches.return_value = ['something', 'matched']
        matches = matches_exist('')
        mock_matches.assert_called_with('')
        self.assertEquals(matches, True)

    @mock.patch('adapters.certuk_mod.visualiser.graph.matches_exist')
    @mock.patch('adapters.certuk_mod.visualiser.graph.backlinks_exist')
    def test_create_graph_show_edges(self, mock_backlinks_exist, mock_matches_exist):
        mock_edge = mock.create_autospec(EdgeObject, id_='matt', summary={'title': ''}, ty='ind', edges=[])
        stack = [(0, None, mock_edge, 'edge')]
        mock_backlinks_exist.return_value = False
        mock_matches_exist.return_value = False
        response = create_graph(stack, [], [], [], [])
        correct_nodes = {'id': 'matt', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': False}
        self.assertDictEqual(response['nodes'][0], correct_nodes)
        self.assertEquals(response['links'], [])

    def test_create_graph_external_ref(self):
        mock_edge = mock.create_autospec(EdgeObject, id_='matt', summary={'title':''}, ty='ind', edges=[])
        stack = [(0, None, mock_edge, 'external_ref')]
        response = create_graph(stack, [], [], [], [])
        correct_nodes = {'id': 'matt', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'external_ref', 'has_matches': False}
        self.assertDictEqual(response['nodes'][0], correct_nodes)
        self.assertEquals(response['links'], [])

    @mock.patch('adapters.certuk_mod.visualiser.graph.matches_exist')
    @mock.patch('adapters.certuk_mod.visualiser.graph.backlinks_exist')
    def test_create_graph_with_backlinks(self, mock_backlinks_exist, mock_matches_exist):
        mock_edge = mock.create_autospec(EdgeObject, id_='purple', summary={'title': ''}, ty='ind', edges=[])
        bl_ids = ['purple']
        mock_backlinks_exist.return_value, mock_matches_exist.return_value = True, False
        stack = [(0, None, mock_edge, 'backlink')]
        response = create_graph(stack, bl_ids, [], [], [])
        correct_nodes = {'id': 'purple', 'backlinks_shown': True, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': True, 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': False}

        self.assertDictEqual(response['nodes'][0], correct_nodes)
        self.assertEquals(response['links'], [])
