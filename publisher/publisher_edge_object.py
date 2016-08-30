from edge.generic import EdgeObject
from edge.scanner import STIXScanner
from users.models import Repository_User
from mongoengine import DoesNotExist


class PublisherEdgeObject(EdgeObject):
    id_alias_separator = ':'

    def __init__(self, doc, filters=None):
        super(PublisherEdgeObject, self).__init__(doc, filters)
        self.created_by_username = ""
        if doc is not None:
            try:
                u = Repository_User.objects(id=doc.get('created_by', ''))
                self.created_by_username = u.get().username
            except DoesNotExist:
                return

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

    @classmethod
    def load_and_parse(cls, selector, filters=None):
        eo = super(PublisherEdgeObject, cls).load(selector, filters)
        doc = PublisherEdgeObject.strip_uuids_from_identities(eo.doc)
        return cls(doc, filters)

    @staticmethod
    def strip_uuids_from_identities(doc):
        def nested_get_sector(identity):
            return identity.get('specification', {}).get('organisation_info', {}).get(
                'industry_type', '')

        if 'identity' in doc['data']['api'].get('reporter', {}):
            doc['data']['api']['reporter']['identity']['name'] = 'null:%s' % nested_get_sector(
                doc['data']['api']['reporter']['identity'])

        for responder in doc['data']['api'].get('responders', []):
            responder.get('identity', responder)['name'] = 'null:%s' % nested_get_sector(
                responder.get('identity', responder))

        for victim in doc['data']['api'].get('victims', []):
            victim.get('identity', victim)['name'] = 'null:%s' % nested_get_sector(victim.get('identity', victim))

        for co_ordinator in doc['data']['api'].get('coordinators', []):
            co_ordinator.get('identity', co_ordinator)['name'] = 'null:%s' % nested_get_sector(
                co_ordinator.get('identity', co_ordinator))

        return doc
