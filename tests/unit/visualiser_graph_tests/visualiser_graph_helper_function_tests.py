import mock
import unittest
from pymongo.cursor import Cursor

from adapters.certuk_mod.visualiser.graph import matches_exist, backlinks_exist


class VisualiserGraphMatchesBacklinksTests(unittest.TestCase):

    @mock.patch('adapters.certuk_mod.visualiser.graph.get_matches')
    def test_matches_do_not_exist(self, mock_get_matches):
        mock_get_matches.return_value = []
        matches = matches_exist('')
        mock_get_matches.assert_called_with('')
        self.assertEquals(matches, False)

    @mock.patch('adapters.certuk_mod.visualiser.graph.get_matches')
    def test_matches_do_exist(self, mock_get_matches):
        mock_get_matches.return_value = ['something', 'matched']
        matches = matches_exist('purple')
        mock_get_matches.assert_called_with('purple')
        self.assertEquals(matches, 2)

    @mock.patch('adapters.certuk_mod.visualiser.graph.get_backlinks')
    def test_backlinks_do_not_exist(self, mock_get_backlinks):
        db_obj = mock.create_autospec(Cursor)
        db_obj.count.return_value = 0
        mock_get_backlinks.return_value = db_obj
        backlinks = backlinks_exist('')
        mock_get_backlinks.assert_called_with('')
        self.assertEquals(backlinks, False)

    @mock.patch('adapters.certuk_mod.visualiser.graph.get_backlinks')
    def test_backlinks_do_exist(self, mock_get_backlinks):
        db_obj = mock.create_autospec(Cursor)
        db_obj.count.return_value = 1
        mock_get_backlinks.return_value = db_obj
        backlinks = backlinks_exist('purple')
        mock_get_backlinks.assert_called_with('purple')
        self.assertEquals(backlinks, True)
