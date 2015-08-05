
from edge import LOCAL_ALIAS, LOCAL_NAMESPACE
from mongoengine.connection import get_db
from bson import ObjectId


class PublisherConfig(object):

    @staticmethod
    def update_config(data):
        # For now, just store an extra flag against the peer_site documents.
        # In practice, we'd probably want a mongo collection specifically for adapter config.
        # ...in which case, we'd probably just save the ID of the publish site instead.
        site_id = data['site_id']
        object_site_id = None
        unset_sites = {}

        if site_id:
            object_site_id = ObjectId(site_id)
            unset_sites['_id'] = {'$ne': object_site_id}

        db = get_db()

        if object_site_id is not None:
            db.peer_sites.update({
                '_id': object_site_id
            }, {
                '$set': {'is_publish_site': True}
            })

        db.peer_sites.update(unset_sites, {
            '$set': {'is_publish_site': False}
        }, multi=True)


    @staticmethod
    def get_sites():
        sites = []
        for site in get_db().peer_sites.find():
            sites.append({
                'site_id': str(site['_id']),
                'name': site['name'],
                'url': site['url'],
                'discovery_state': site['discovery_state'],
                'is_publish_site': site.get('is_publish_site', False)
            })

        return sites

    @staticmethod
    def get_config():
        site_id = None
        site = get_db().peer_sites.find_one({'is_publish_site': True})
        if site is not None:
            site_id = site['_id']

        return {
            'site_id': site_id,
            'namespace_id': LOCAL_NAMESPACE,
            'namespace_alias': LOCAL_ALIAS,
            'valid_root_types': {
                'ind': True,
                'cam': False,
                'act': False,
                'ttp': False,
                'tgt': False,
                'inc': True,
                'obs': False,
                'coa': False
            }
        }

