import unittest

from adapters.certuk_mod.patch.capsulize_patch import capsulize_patch
import mock
from edge.generic import EdgeError


class CapsualizePatchTests(unittest.TestCase):

    @mock.patch('adapters.certuk_mod.patch.capsulize_patch.EdgeObject')
    def testSimple(self, mock_EdgeObject):

        mock_ind = mock.MagicMock()
        mock_obs = mock.MagicMock()

        with mock.patch.dict('adapters.certuk_mod.patch.capsulize_patch.PACKAGE_ADD_DISPATCH', {'ind': mock_ind, 'obs': mock_obs}):
            eo = mock.MagicMock()
            eo.ty = 'ind'
            eo_child = mock.MagicMock()
            eo_child.ty = 'obs'
            eo_child.id = "1"
            mock_EdgeObject.load.side_effect = [eo_child]
            eo.edges = [eo_child]
            pkg, contents = capsulize_patch(eo, 1, False)
            mock_ind.assert_called_once()
            mock_obs.assert_not_called()
            self.assertEqual(len(contents), 1)

    @mock.patch('adapters.certuk_mod.patch.capsulize_patch.EdgeObject')
    def testSimpleBfs(self, mock_EdgeObject):

        mock_ind = mock.MagicMock()
        mock_obs = mock.MagicMock()

        with mock.patch.dict('adapters.certuk_mod.patch.capsulize_patch.PACKAGE_ADD_DISPATCH', {'ind': mock_ind, 'obs': mock_obs}):
            eo = mock.MagicMock()
            eo.ty = 'ind'
            eo_child = mock.MagicMock()
            eo_child.ty = 'obs'
            eo_child.id = "1"
            mock_EdgeObject.load.side_effect = [eo_child]
            eo.edges = [eo_child]
            pkg, contents = capsulize_patch(eo, 1, True)
            mock_ind.assert_called_once()
            mock_obs.assert_called_once()
            self.assertEqual(len(contents), 2)

    @mock.patch('adapters.certuk_mod.patch.capsulize_patch.EdgeObject')
    def testLoopedBfs(self, mock_EdgeObject):

        mock_ind = mock.MagicMock()
        mock_obs = mock.MagicMock()

        with mock.patch.dict('adapters.certuk_mod.patch.capsulize_patch.PACKAGE_ADD_DISPATCH', {'ind': mock_ind, 'obs': mock_obs}):
            eo = mock.MagicMock()
            eo.ty = 'ind'
            eo_child = mock.MagicMock()
            eo_child.ty = 'obs'
            eo_child.id = "1"
            eo_child.edges = [eo]
            mock_EdgeObject.load.side_effect = [eo_child]
            eo.edges = [eo_child]
            pkg, contents = capsulize_patch(eo, 1, True)
            mock_ind.assert_called_once()
            mock_obs.assert_called_once()
            self.assertEqual(len(contents), 2)

    @mock.patch('adapters.certuk_mod.patch.capsulize_patch.EdgeObject')
    def testExternalReference(self, mock_EdgeObject):

        mock_ind = mock.MagicMock()
        mock_obs = mock.MagicMock()

        with mock.patch.dict('adapters.certuk_mod.patch.capsulize_patch.PACKAGE_ADD_DISPATCH', {'ind': mock_ind, 'obs': mock_obs}):
            eo = mock.MagicMock()
            eo.ty = 'ind'
            eo_child = mock.MagicMock()
            eo_child.ty = 'obs'
            eo_child.id = "1"
            eo_child.edges = [eo]

            def raise_EdgeError(x):
                raise EdgeError;

            mock_EdgeObject.load = raise_EdgeError
            eo.edges = [eo_child]
            pkg, contents = capsulize_patch(eo, 1, True)
            mock_ind.assert_called_once()
            self.assertEqual(len(contents), 1)
