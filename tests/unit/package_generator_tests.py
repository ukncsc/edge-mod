
import unittest
import mock
from import_helper import EdgeObject
from package_generator import PackageGenerator


class PackageGeneratorTests(unittest.TestCase):

    @mock.patch('stix.core.STIXPackage', autospec=True)
    @mock.patch('package_generator.IDManager')
    @mock.patch(EdgeObject.__module__ + '.' + EdgeObject.__name__, autospec=True)
    def test_BuildPackage_WhenCalled_SetCorrectPackageProperties(self, mock_edge_object, mock_id_generator,
                                                                 mock_package):
        package_id = 'Dummy package ID'
        mock_edge_object.capsulize.return_value = (mock_package, {})
        mock_id_generator.return_value.get_new_id.return_value = package_id

        package_info = {
            'title': 'Dummy title',
            'short_description': 'Dummy short description',
            'description': 'Dummy description'
        }
        package = PackageGenerator.build_package(mock_edge_object, package_info)

        self.assertEqual(mock_edge_object.capsulize.call_args[1]['pkg_id'], package_id)
        self.assertEqual(package.stix_header.title, package_info['title'])
        self.assertEqual(package.stix_header.short_description.value, package_info['short_description'])
        self.assertEqual(package.stix_header.description.value, package_info['description'])


if __name__ == '__main__':
    unittest.main()
