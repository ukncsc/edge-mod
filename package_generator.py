
from stix.core import STIXHeader
from edge import IDManager


class PackageGenerator(object):

    @staticmethod
    def build_package(edge_object, package_info):
        (stix_package, package_contents) = edge_object.capsulize(pkg_id=IDManager().get_new_id('Package'),
                                                                 enable_bfs=True)

        stix_package.stix_header = STIXHeader(title=package_info.get('title'),
                                              short_description=package_info.get('short_description'),
                                              description=package_info.get('description'))

        return stix_package
