
import mock


def mock_get_json_config_by_key(key):
    if key == 'company_alias':
        return 'DummyAlias'
    if key == 'company_namespace':
        return 'DummyNamespace'
    return ''

BASE_DIR = ''
SECRET_KEY = ')gmpt=zx@(73$3=%#@p9@ucm--d#a%f(z-j6ws+nkvxgk4n9&*'

MONGO_DIR = 'MongoDir'
MONGO_DB_NAME = 'MongoDBName'
MONGO_DB_PORT = 1234
MONGO_DB_HOST = 'MongoDBHost'

ACTIVE_CONFIG = mock.patch('jsonconfig.JsonConfig', autospec=True).start()
ACTIVE_CONFIG.by_key.side_effect = mock_get_json_config_by_key


def REPOCONFIG():
    return ACTIVE_CONFIG

mock.patch('mongoengine.connection.get_db', autospec=True).start()

RUNNING_ADAPTERS = ()
