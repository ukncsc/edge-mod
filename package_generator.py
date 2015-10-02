
from stix.core import STIXHeader
from edge import IDManager


class PackageGenerator(object):

    @staticmethod
    def build_package(edge_object):
        (stix_package, package_contents) = edge_object.capsulize(pkg_id=IDManager().get_new_id('Package'),
                                                                 enable_bfs=True)

        return stix_package
