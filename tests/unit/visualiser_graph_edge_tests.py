import unittest
import mock

from edge.generic import EdgeObject, EdgeReference
from adapters.certuk_mod.visualiser.graph import create_graph


class VisualiserGraphNodeTests(unittest.TestCase):
    def setUp(self):
        self.mock_build_title_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.build_title')
        self.mock_backlinks_exist_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.backlinks_exist')
        self.mock_matches_exist_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.matches_exist')
        self.mock_get_backlinks_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.get_backlinks')
        self.mock_get_matches_patcher = mock.patch('adapters.certuk_mod.visualiser.graph.get_matches')

        self.mock_build_title = self.mock_build_title_patcher.start()
        self.mock_backlinks_exist = self.mock_backlinks_exist_patcher.start()
        self.mock_matches_exist = self.mock_matches_exist_patcher.start()
        self.mock_get_backlinks = self.mock_get_backlinks_patcher.start()
        self.mock_get_matches = self.mock_get_matches_patcher.start()

        self.init_stix_objects()

    def tearDown(self):
        self.mock_build_title_patcher.stop()
        self.mock_backlinks_exist_patcher.stop()
        self.mock_matches_exist_patcher.stop()
        self.mock_get_backlinks_patcher.stop()
        self.mock_get_matches_patcher.stop()

    def init_stix_objects(self):
        self.mock_edge_title_None = mock.create_autospec(EdgeObject, id_='matt', summary={'title': None}, ty='ind', edges=[])
        self.mock_edge = mock.create_autospec(EdgeObject, id_='purple', summary={'title': ''}, ty='ind', edges=[])

        self.edge_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.edge_node2 = {'id': 'matt', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': self.mock_backlinks_exist(), 'has_edges': True, 'matches_shown': False, 'title': '',
                              'type': 'coa', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.matching_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': False,
                              'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': True, 'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.backlink_node = {'id': 'purple', 'backlinks_shown': True, 'depth': 0, 'edges_shown': False,
                              'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.external_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'external_ref', 'has_matches': False}

        self.draft_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'draft', 'has_matches': False}

        self.mock_edge_reference = mock.create_autospec(EdgeReference, id_='purple', ty='ind')
        self.mock_edge2 = mock.create_autospec(EdgeObject, id_='matt', summary={'title': ''}, ty='coa', edges=[self.mock_edge_reference])

    def test_create_graph_build_title_called(self ):
        stack = [(0, None, self.mock_edge_title_None, 'edge')]
        create_graph(stack, [], [], [], [])
        self.mock_build_title.assert_called_with(self.mock_edge_title_None)

    def test_create_graph_backlinks_matches_called(self):
        stack = [(0, None, self.mock_edge, 'edge')]
        create_graph(stack, [], [], [], [])
        self.mock_backlinks_exist.assert_called_with('purple')
        self.mock_matches_exist.assert_called_with('purple')

    def test_create_graph_with_edge_rel_type(self):
        stack = [(0, None, self.mock_edge, 'edge')]
        response = create_graph(stack, [], [], [], [])
        self.assertEquals(response['nodes'], [self.edge_node])
        self.assertEquals(response['links'], [])

    def test_create_graph_with_links(self):
        self.mock_edge_reference.fetch.return_value = self.mock_edge
        stack = [(0, None, self.mock_edge2, 'edge')]
        response = create_graph(stack, [], [], [], [])
        links = [{'source': 0, 'target': 1, 'rel_type': 'edge'}]
        self.assertDictEqual(response['nodes'][0], self.edge_node2)
        self.assertDictEqual(response['nodes'][1], self.edge_node)
        self.assertEquals(response['links'], links)






    # @mock.patch('adapters.certuk_mod.visualiser.graph.matches_exist')
    # @mock.patch('adapters.certuk_mod.visualiser.graph.backlinks_exist')
    # def test_create_graph_show_edges(self, mock_backlinks_exist, mock_matches_exist):
    #     mock_edge = mock.create_autospec(EdgeObject, id_='matt', summary={'title': ''}, ty='ind', edges=[])
    #     stack = [(0, None, mock_edge, 'edge')]
    #     mock_backlinks_exist.return_value = False
    #     mock_matches_exist.return_value = False
    #     response = create_graph(stack, [], [], [], [])
    #     correct_nodes = {'id': 'matt', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
    #                           'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': '',
    #                           'type': 'ind', 'node_type': 'normal', 'has_matches': False}
    #     self.assertDictEqual(response['nodes'][0], correct_nodes)
    #     self.assertEquals(response['links'], [])


