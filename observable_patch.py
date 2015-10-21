
import edge.observable as patch_target
from edge.observable import DBObservable as OriginalDBObservable, get_obs_value as original_get_obs_value
from edge.tools import rgetattr


class DBObservablePatch(OriginalDBObservable):

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
    def _http_session_to_draft(observable, tg, load_by_id, id_ns = ''):
        return {
                'objectType': 'HTTP Session',
                'id': rgetattr(observable, ['id_'], ''),
                'id_ns': id_ns,
                'title': rgetattr(observable, ['title'], ''),
                'description': str(rgetattr(observable, ['description'], '')),
                'user_agent': str(rgetattr(observable, ['http_request_response', 'http_client_request',
                                                        'http_request_header', 'parsed_header', 'user_agent'], ''))
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


def get_http_session_object_value(obj):
    return rgetattr(obj, ['http_request_response', 'http_client_request', 'http_request_header', 'parsed_header',
                          'user_agent'], None)

custom_object_value_map = {
    'HTTPSessionObjectType': get_http_session_object_value
}


def custom_get_obs_value(obj):
    type_ = rgetattr(obj, ['object_', 'properties', '_XSI_TYPE'], None)
    custom_type_handler = custom_object_value_map.get(type_)
    if custom_type_handler is None:
        return original_get_obs_value(obj)
    return custom_type_handler(obj)


# Will this work..!?
patch_target.DBObservable = DBObservablePatch
patch_target.get_obs_value = custom_get_obs_value
