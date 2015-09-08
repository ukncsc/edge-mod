
from import_helper import EdgeObject
from edge.scanner import STIXScanner


class PublisherEdgeObject(EdgeObject):

    id_alias_separator = ':'

    def __init__(self, doc, filters=None):
        super(PublisherEdgeObject, self).__init__(doc, filters)

    def ns_dict(self):
        namespaces = {}
        for edge_object in STIXScanner({'_id': self.id_}, self.filters):
            id_parts = edge_object.id_.split(PublisherEdgeObject.id_alias_separator)
            if len(id_parts) == 2:
                alias = id_parts[0]
                namespaces[edge_object.id_ns] = alias
            elif len(id_parts) > 2:
                raise Exception("Malformed ID")

        return namespaces
