from edge import IDManager, NamespaceNotConfigured
from edge.tools import Optional
from users.models import Repository_User


class Revocable(object):

    def __init__(self, edge_object, request):
        self.edge_object = edge_object
        self.request = request
        self.namespace = self.get_namespace()

    @staticmethod
    def get_namespace():
        try:
            system_id_ns = IDManager().get_namespace()
        except NamespaceNotConfigured:
            system_id_ns = None
        return system_id_ns

    def is_revocable(self):
        created_by_organization = Optional(Repository_User).objects.get(id=self.edge_object.doc['created_by']).organization.value()

        return (
            self.edge_object.id_ns == self.namespace and
            self.request.user.organization is not None and
            created_by_organization == self.request.user.organization and
            self.edge_object.ty in ['ttp', 'cam', 'act', 'coa', 'tgt', 'inc', 'ind']
        )
