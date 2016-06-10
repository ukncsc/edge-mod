import unittest
import mock

from edge.generic import EdgeObject, EdgeReference, EdgeError
from adapters.certuk_mod.visualiser.graph import create_graph


class VisualiserGraphExternalRefTests(unittest.TestCase):

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
        self.mock_edge = mock.create_autospec(EdgeObject, id_='purple', summary={'title': ''}, ty='ind', edges=[])

        self.edge_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                          'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': False,
                          'title': '',
                          'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.external_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'external_ref', 'has_matches': False}


        self.mock_external_ref = mock.create_autospec(EdgeReference, id_='purple', ty='ind')
        self.mock_edge2 = mock.create_autospec(EdgeObject, id_='matt', summary={'title': ''}, ty='coa',
                                               edges=[self.mock_external_ref])

        self.edge_node2 = {'id': 'matt', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                          'has_backlinks': self.mock_backlinks_exist(), 'has_edges': True, 'matches_shown': False,
                          'title': '',
                          'type': 'coa', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.external_node2 = {'id': 'purple', 'backlinks_shown': False, 'depth': 1, 'edges_shown': True,
                           'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': 'purple',
                           'type': 'ind', 'node_type': 'external_ref', 'has_matches': False}

        self.draft_node = {'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                          'has_backlinks': False, 'has_edges': False, 'matches_shown': False,
                          'title': '',
                          'type': 'ind', 'node_type': 'draft', 'has_matches': False}


    def test_create_graph_with_external_ref_rel_type(self):
        stack = [(0, None, self.mock_edge, 'external_ref')]
        response = create_graph(stack, [], [], [], [])
        self.assertEquals(response['nodes'], [self.external_node])
        self.assertEquals(response['links'], [])

    def test_create_graph_external_ref_link(self):
        self.mock_external_ref.fetch.side_effect = EdgeError('purple not found')
        stack = [(0, None, self.mock_edge2, 'edge')]
        response = create_graph(stack, [], [], [], [])
        links = [{'source': 0, 'target': 1, 'rel_type': 'external_ref'}]
        self.assertEquals(response['nodes'][0], self.edge_node2)
        self.assertEquals(response['nodes'][1], self.external_node2)
        self.assertEquals(response['links'], links)

    def test_create_graph_with_draft_rel_type(self):
        stack = [(0, None, self.mock_edge, 'draft')]
        response = create_graph(stack, [], [], [], [])
        self.assertEquals(response['nodes'], [self.draft_node])


