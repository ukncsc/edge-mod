
from stix.core import STIXHeader
from edge import IDManager
from edge.edge_object import EdgeObject


class PackageGenerator(object):

    @staticmethod
    def build_package(object_id, package_info):
        edge_object = EdgeObject.load(object_id)
        (stix_package, package_contents) = edge_object.capsulize(pkg_id=PackageGenerator._generate_package_id(),
                                                                 enable_bfs=True)

        stix_package.stix_header = PackageGenerator._generate_stix_header(package_info.get('title'),
                                                                          package_info.get('short_description'),
                                                                          package_info.get('description'))

        return stix_package

    @staticmethod
    def _generate_package_id():
        return IDManager().get_new_id('Package')

    @staticmethod
    def _generate_stix_header(title, short_description, description):
        return STIXHeader(title=title, short_description=short_description, description=description)
