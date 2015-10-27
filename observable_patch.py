from edge.generic import WHICH_DBOBJ
from edge.observable import \
    CYBOX_SHORT_DESCRIPTION, \
    DBObservable, \
    get_obs_value as original_get_obs_value, \
    get_obs_type as original_get_obs_type, \
    get_obs_title as original_get_obs_title, \
    get_obs_description as original_get_obs_description
from edge.tools import rgetattr


def get_http_session_object_value(obj):
    http_request_response_list = rgetattr(obj, ['_object', 'properties', 'http_request_response'])
    value = rgetattr(http_request_response_list[0],
                    ['http_client_request', 'http_request_header', 'parsed_header', 'user_agent'], '(undefined)')
    return str(value)


custom_object_value_map = {
    'HTTPSessionObjectType': get_http_session_object_value
}


def custom_get_obs_value(obj):
    type_ = rgetattr(obj, ['object_', 'properties', '_XSI_TYPE'], None)
    custom_type_handler = custom_object_value_map.get(type_)
    if custom_type_handler is None:
        return original_get_obs_value(obj)
    return custom_type_handler(obj)


DBObservable.SUMMARY_BINDING = (
    ('type', original_get_obs_type),
    ('title', original_get_obs_title),
    ('description', original_get_obs_description),
    ('value', custom_get_obs_value),
)


class DBObservablePatch(DBObservable):
    def __init__(self, obj=None, item=None, id_=None):
        super(DBObservablePatch, self).__init__(obj, item, id_)

    @staticmethod
    def _get_custom_to_draft_handler(object_type):
        handler_map = {
            'HTTPSessionObjectType': DBObservablePatch._http_session_to_draft
        }
        try:
            return handler_map[object_type]
        except KeyError:
            raise ValueError("Unexpected Object Type %s" % object_type)

    @staticmethod
    def _http_session_to_draft(observable, tg, load_by_id, id_ns=''):
        return {
            'objectType': 'HTTP Session',
            'id': rgetattr(observable, ['id_'], ''),
            'id_ns': id_ns,
            'title': rgetattr(observable, ['title'], ''),
            'description': str(rgetattr(observable, ['description'], '')),
            'user_agent': get_http_session_object_value(observable)
        }

    @classmethod
    def to_draft(cls, observable, tg, load_by_id, id_ns=''):
        try:
            return super(DBObservablePatch, cls).to_draft(observable, tg, load_by_id, id_ns=id_ns)
        except ValueError:
            pass

        object_type = rgetattr(observable, ['_object', '_properties', '_XSI_TYPE'], 'None')
        draft_handler = DBObservablePatch._get_custom_to_draft_handler(object_type)
        return draft_handler(observable, tg, load_by_id, id_ns)


CYBOX_SHORT_DESCRIPTION['HTTPSessionObjectType'] = 'HTTP Session'
WHICH_DBOBJ['obs'] = DBObservablePatch
