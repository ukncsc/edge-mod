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
        self.mock_request_patcher = mock.patch('django.http.request.HttpRequest')


        self.mock_build_title = self.mock_build_title_patcher.start()
        self.mock_backlinks_exist = self.mock_backlinks_exist_patcher.start()
        self.mock_matches_exist = self.mock_matches_exist_patcher.start()
        self.mock_get_backlinks = self.mock_get_backlinks_patcher.start()
        self.mock_get_matches = self.mock_get_matches_patcher.start()
        self.mock_request = self.mock_request_patcher.start()

        self.init_stix_objects()

    def tearDown(self):
        self.mock_build_title_patcher.stop()
        self.mock_backlinks_exist_patcher.stop()
        self.mock_matches_exist_patcher.stop()
        self.mock_get_backlinks_patcher.stop()
        self.mock_get_matches_patcher.stop()

    def init_stix_objects(self):
        self.mock_edge_reference = mock.create_autospec(EdgeReference, id_='purple', ty='ind')
        self.mock_edge_title_None = mock.create_autospec(EdgeObject, id_='matt', summary={'title': None}, ty='ind',
                                                         edges=[])

        self.mock_edge = mock.create_autospec(EdgeObject, id_='red', summary={'title': ''}, ty='ind', edges=[])
        self.mock_edge2 = mock.create_autospec(EdgeObject, id_='orange', summary={'title': ''}, ty='coa',
                                               edges=[self.mock_edge_reference])
        self.mock_edge3 = mock.create_autospec(EdgeObject, id_='green', summary={'title': ''}, ty='ind', edges=[])
        self.mock_edge4 = mock.create_autospec(EdgeObject, id_='blue', summary={'title': ''}, ty='ind',
                                               edges=['edge1', 'edge2'])
        self.mock_edge5 = mock.create_autospec(EdgeObject, id_='orange', summary={'title': ''}, ty='ind',
                                               edges=[])

        self.edge_node = {'id': 'red', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                          'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': False,
                          'title': '',
                          'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.edge_node2 = {'id': 'orange', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                           'has_backlinks': self.mock_backlinks_exist(), 'has_edges': True, 'matches_shown': False,
                           'title': '',
                           'type': 'coa', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.edge_node3 = {'id': 'green', 'backlinks_shown': False, 'depth': 1, 'edges_shown': True,
                           'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': False,
                           'title': '',
                           'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.edge_node4 = {'id': 'blue', 'backlinks_shown': False, 'depth': 0, 'edges_shown': False,
                           'has_backlinks': self.mock_backlinks_exist(), 'has_edges': True, 'matches_shown': False,
                           'title': '',
                           'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

        self.edge_node5 = {'id': 'orange', 'backlinks_shown': False, 'depth': 1, 'edges_shown': True,
                           'has_backlinks': self.mock_backlinks_exist(), 'has_edges': True, 'matches_shown': False,
                           'title': '',
                           'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}

    def test_create_graph_build_title_called(self):
        stack = [(0, None, self.mock_edge_title_None, 'edge')]
        create_graph(stack, [], [], [], [], [], self.mock_request)
        self.mock_build_title.assert_called_with(self.mock_edge_title_None)

    def test_create_graph_backlinks_matches_called(self):
        stack = [(0, None, self.mock_edge, 'edge')]
        create_graph(stack, [], [], [], [], [], self.mock_request)
        self.mock_backlinks_exist.assert_called_with('red')
        self.mock_matches_exist.assert_called_with('red', self.mock_request)

    def test_create_graph_with_edge_rel_type(self):
        stack = [(0, None, self.mock_edge, 'edge')]
        response = create_graph(stack, [], [], [], [], [], self.mock_request)
        self.assertEquals(response['nodes'], [self.edge_node])
        self.assertEquals(response['links'], [])

    def test_create_graph_with_links(self):
        self.mock_edge_reference.fetch.return_value = self.mock_edge3
        stack = [(0, None, self.mock_edge2, 'edge')]
        response = create_graph(stack, [], [], [], [], [], self.mock_request)
        links = [{'source': 0, 'target': 1, 'rel_type': 'edge'}]
        self.assertDictEqual(response['nodes'][0], self.edge_node2)
        self.assertDictEqual(response['nodes'][1], self.edge_node3)
        self.assertEquals(response['links'], links)

    def test_create_graph_hide_edge_ids(self):
        hide_edge_ids = ['blue']
        stack = [(0, None, self.mock_edge4, 'edge')]
        response = create_graph(stack, [], [], hide_edge_ids, [], [], self.mock_request)
        self.assertEquals(response['nodes'], [self.edge_node4])
        self.assertEquals(response['links'], [])

    def test_create_graph_show_edges_ids(self):
        show_edge_ids = ['red']
        stack = [(0, None, self.mock_edge, 'edge')]
        response = create_graph(stack, [], [], [], show_edge_ids, [], self.mock_request)
        self.assertEquals(response['nodes'], [self.edge_node])
        self.assertEquals(response['links'], [])

    def test_create_graph_hide_ids(self):
        hide_ids = ['blue']
        stack = [(0, None, self.mock_edge4, 'edge')]
        response = create_graph(stack, [], [], [], [], hide_ids, self.mock_request)
        self.assertEquals(response['nodes'], [])
        self.assertEquals(response['links'], [])

    def test_create_graph_existing_id(self):
        stack = [(0, None, self.mock_edge2, 'edge')]
        self.mock_edge_reference.fetch.return_value = self.mock_edge5
        links = [{'source': 0, 'target': 0, 'rel_type': 'edge'}]
        response = create_graph(stack, [], [], [], [], [], self.mock_request)
        self.assertEqual(len(response['nodes']), 1)
        self.assertEqual(response['nodes'], [self.edge_node2])
        self.assertEqual(response['links'], links)
