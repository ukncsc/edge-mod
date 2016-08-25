from mongoengine.connection import get_db
from edge.generic import EdgeObject, EdgeError
from edge.scanner import STIXScanner
from users.models import Repository_User
from mongoengine import DoesNotExist
from dateutil import parser
from copy import deepcopy

SUBDOCS = {'type': 1, 'data': 1, '_id': 1, 'cv': 1, 'created_on': 1, 'created_by': 1, 'tg': 1,
           'created_by_organization': 1, 'versions': 1}


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
    def load(cls, selector, filters=None, revision='latest', include_revision_index=False, publish_externally=False):
        version_string = lambda x: "data_%s" % x

        def _extract_index(doc):
            doc['revision_index'] = []
            CHUNK_SIZE = 20

            """ We start by breaking the list of timekeys from doc['versions'] into a chunked
            list of lists of timekeys with that goofy-looking comprehension which breaks
            this version list into sublists of 20 versions and stores that as revision_chunks """

            revision_chunks = [doc['versions'][x:x + CHUNK_SIZE] for x in range(0, len(doc['versions']), CHUNK_SIZE)]

            for batch in revision_chunks:
                """ Then, we prepend 'data_' to each of those strings and use that result
                to key the projections dictionary that we will pass through to Mongo.
                This means that the size of the package returned is controllable; we don't
                have to load every revision. """
                projections = {version_string(timekey): 1 for timekey in batch}
                projections.update({'created_on': 1})
                batch_docs = get_db().stix.find_one({'_id': selector}, projections)
                for timekey in batch:
                    # For each revision, we resolve the 'username' string and parse out the timesamp
                    # it should be noted that `rgetattr` wasn't resolving this and since prior
                    # to 2.5, Edge didn't store the key, the exception handling becomes necessary
                    try:
                        versionkey = version_string(timekey)
                        username = batch_docs[versionkey].get('created_by', 'unknown')
                        if 'timestamp' in batch_docs[versionkey]['api'].keys():
                            timestamp = parser.parse(batch_docs[versionkey]['api']['timestamp'])

                        else:
                            timestamp = batch_docs['created_on']

                        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    except KeyError:
                        username = 'unknown'

                    # Then we build the index entry dict for this revision.
                    doc['revision_index'].append({'timekey': timekey,
                                                  'timestamp': timestamp,
                                                  'author': username,
                                                  'label': "{} ~ {}".format(timestamp, username),
                                                  'is_latest': timekey == doc['cv'],
                                                  })

            doc['revision_index'].sort(key=lambda x: x['timestamp'], reverse=True)
            return doc

        query = {}
        if filters:
            query.update(filters)
        query['_id'] = selector

        doc = None
        if revision != 'latest':
            """ If you need a specific revision...

            We want to be able to get the document in a single Mongo read, so the
            first thing we do is copy the normal `SUBDOCS` projection and add
            the revision to that list.  Then when we pull the document and
            assert that we got that key back before copying that key's value
            into doc['data'] and add the key for the revision being loaded.
            """
            custom_projection = deepcopy(SUBDOCS)
            target_version_string = "data_%s" % revision
            custom_projection.update({target_version_string: 1})
            doc = get_db().stix.find_one(query, custom_projection)
            assert target_version_string in doc.keys(), "%s did not raise a valid revision" % target_version_string

            doc['data'] = doc[target_version_string]
            doc['this_revision'] = revision
        else:  # ... otherwise continue as we always have
            doc = get_db().stix.find_one(query, SUBDOCS)

        if not doc:
            raise EdgeError("%s not found" % selector)

        if include_revision_index:
            doc = _extract_index(doc)

        if publish_externally:
            if doc['type'] == 'inc':
                PublisherEdgeObject.strip_uuids_from_identities(doc)

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
