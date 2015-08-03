
from edge import LOCAL_ALIAS, LOCAL_NAMESPACE


class PublisherConfig(object):

    @staticmethod
    def update_config(data):
        pass

    @staticmethod
    def get_config():
        return {
            'site_id': '55b7b76b34550739a0c860dc',
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
