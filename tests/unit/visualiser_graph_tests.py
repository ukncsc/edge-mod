import mock
import unittest

from adapters.certuk_mod.visualiser.graph import build_title, get_backlinks, get_matches, backlinks_exist, matches_exist, \
    create_graph

from edge.generic import EdgeObject, EdgeReference


class VisualiserGraphTests(unittest.TestCase):
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
        self.mock_edge = mock.create_autospec(EdgeObject, id_='matt', summary={'title': ''}, ty='ind', edges=[])
        self.mock_edge_match = mock.create_autospec(EdgeObject, id_='purple', summary={'title': ''}, ty='ind', edges=[])

    def test_matches_do_not_exist(self):
        self.mock_get_matches.return_value = []
        matches = matches_exist('')
        self.mock_get_matches.assert_called_with('')
        self.assertEquals(matches, False)

    def test_matches_do_exist(self):
        self.mock_get_matches.return_value = ['something', 'matched']
        matches = matches_exist('purple')
        self.mock_get_matches.assert_called_with('purple')
        self.assertEquals(matches, True)

    def test_create_graph_build_title(self ):
        stack = [(0, None, self.mock_edge_title_None, 'edge')]
        create_graph(stack, [], [], [], [])
        self.mock_build_title.assert_called_with(self.mock_edge_title_None)
        self.mock_backlinks_exist.assert_called_with('matt')
        self.mock_matches_exist.assert_called_with('matt')

    def test_create_graph_external_ref(self):
        self.mock_backlinks_exist.return_value, self.mock_matches_exist.return_value = False, False
        stack = [(0, None, self.mock_edge, 'edge')]
        response = create_graph(stack, [], [], [], [])
        correct_nodes = {'id': 'matt', 'backlinks_shown': False, 'depth': 0, 'edges_shown': True,
                              'has_backlinks': False, 'has_edges': False, 'matches_shown': False, 'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': False}
        self.assertDictEqual(response['nodes'][0], correct_nodes)
        self.assertEquals(response['links'], [])

    def test_create_graph_with_backlinks(self):
        bl_ids = ['purple']
        stack = [(0, None, self.mock_edge, 'backlink')]
        create_graph(stack, bl_ids, [], [], [])
        self.mock_backlinks_exist.assert_called_with('matt')
        self.mock_matches_exist.assert_called_with('matt')

    def test_create_graph_with_matches(self):
        id_matches = ['purple']
        stack = [(0, None, self.mock_edge_match, 'match')]
        response = create_graph(stack, [], id_matches, [], [])
        correct_nodes = [{'id': 'purple', 'backlinks_shown': False, 'depth': 0, 'edges_shown': False,
                              'has_backlinks': self.mock_backlinks_exist(), 'has_edges': False, 'matches_shown': True, 'title': '',
                              'type': 'ind', 'node_type': 'normal', 'has_matches': self.mock_matches_exist()}]
        self.assertEquals(response['nodes'], correct_nodes)
        self.assertEquals(response['links'], [])

        self.mock_get_matches.assert_called_with('purple')


    # @mock.patch('adapters.certuk_mod.visualiser.graph.matches_exist')
    # @mock.patch('adapters.certuk_mod.visualiser.graph.backlinks_exist')
    # def test_create_graph_with_backlinks(self, mock_backlinks_exist, mock_matches_exist):
    #     mock_edge = mock.create_autospec(EdgeObject, id_='purple', summary={'title': ''}, ty='ind', edges=[])
    #     bl_ids = ['purple']
    #     mock_backlinks_exist.return_value, mock_matches_exist.return_value = True, False
    #     stack = [(0, None, mock_edge, 'backlink')]
    #     response = create_graph(stack, bl_ids, [], [], [])
    #     correct_nodes = {'id': 'matt', 'backlinks_shown': True, 'depth': 0, 'edges_shown': True,
    #                           'has_backlinks': True, 'has_edges': False, 'matches_shown': False, 'title': '',
    #                           'type': 'ind', 'node_type': 'normal', 'has_matches': False}
    #     self.assertDictEqual(response['nodes'][0], correct_nodes)
    #     self.assertEquals(response['links'], [])
    #     mock_backlinks_exist.assert_called_with('matt')
    #     mock_matches_exist.assert_called_with('matt')


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
