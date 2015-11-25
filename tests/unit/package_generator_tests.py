import unittest

import mock

from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from edge.generic import EdgeObject


class PackageGeneratorTests(unittest.TestCase):

    @mock.patch('stix.core.STIXPackage', autospec=True)
    @mock.patch('adapters.certuk_mod.publisher.package_generator.IDManager')
    @mock.patch(EdgeObject.__module__ + '.' + EdgeObject.__name__, autospec=True)
    def test_BuildPackage_WhenCalled_SetCorrectPackageProperties(self, mock_edge_object, mock_id_generator,
                                                                 mock_package):
        package_id = 'Dummy package ID'
        mock_edge_object.capsulize.return_value = (mock_package, {})
        mock_id_generator.return_value.get_new_id.return_value = package_id

        PackageGenerator.build_package(mock_edge_object)

        self.assertEqual(mock_edge_object.capsulize.call_args[1]['pkg_id'], package_id)
