
from stix.core import STIXPackage, STIXHeader
from edge import IDManager
from edge.edge_object import EdgeObject
from edge.generic import PACKAGE_ADD_DISPATCH


class PackageGenerator(object):

    @staticmethod
    def build_package(object_ids, package_info):
        stix_package = STIXPackage(id_=PackageGenerator._generate_package_id(),
                                   stix_header=PackageGenerator._generate_stix_header(package_info.get('title'),
                                                                                      package_info.get(
                                                                                          'short_description'),
                                                                                      package_info.get('description')))

        PackageGenerator._add_objects_to_package(object_ids, stix_package)

        return stix_package

    @staticmethod
    def _generate_package_id():
        return IDManager().get_new_id('Package')

    @staticmethod
    def _generate_stix_header(title, short_description, description):
        return STIXHeader(title=title, short_description=short_description, description=description)

    @staticmethod
    def _add_objects_to_package(object_ids, package):
        for id in object_ids:
            edge_object = EdgeObject.load(id)
            PACKAGE_ADD_DISPATCH[edge_object.ty](package, edge_object.obj)
