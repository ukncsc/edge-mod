from edge.generic import WHICH_DBOBJ
from edge.observable import \
    CYBOX_SHORT_DESCRIPTION, \
    DBObservable, \
    get_obs_value as original_get_obs_value, \
    get_obs_type as original_get_obs_type, \
    get_obs_title as original_get_obs_title, \
    get_obs_description as original_get_obs_description
from edge.tools import rgetattr


def generate_db_observable_patch(custom_draft_handler_map):
    class DBObservablePatch(DBObservable):
        def __init__(self, obj=None, item=None, id_=None):
            super(DBObservablePatch, self).__init__(obj, item, id_)

        CUSTOM_DRAFT_HANDLERS = custom_draft_handler_map

        @staticmethod
        def _get_custom_to_draft_handler(object_type):
            try:
                return DBObservablePatch.CUSTOM_DRAFT_HANDLERS[object_type]
            except KeyError:
                raise ValueError("Unexpected Object Type %s" % object_type)

        @classmethod
        def to_draft(cls, observable, tg, load_by_id, id_ns=''):
            try:
                return super(DBObservablePatch, cls).to_draft(observable, tg, load_by_id, id_ns=id_ns)
            except ValueError, v:
                if v.__class__ != ValueError:
                    raise

            object_type = rgetattr(observable, ['_object', '_properties', '_XSI_TYPE'], 'None')
            draft_handler = DBObservablePatch._get_custom_to_draft_handler(object_type)
            return draft_handler(observable, tg, load_by_id, id_ns)

    return DBObservablePatch


def generate_custom_get_obs_value(custom_object_value_map):
    def custom_get_obs_value(obj):
        type_ = rgetattr(obj, ['object_', 'properties', '_XSI_TYPE'], None)
        custom_type_handler = custom_object_value_map.get(type_)
        if custom_type_handler is None:
            return original_get_obs_value(obj)
        return custom_type_handler(obj)
    return custom_get_obs_value


def apply_patch(custom_observable_definitions):
    custom_draft_handler_map = {}
    custom_summary_value_map = {}

    for definition in custom_observable_definitions:
        custom_draft_handler_map[definition.object_type] = definition.to_draft_handler
        custom_summary_value_map[definition.object_type] = definition.summary_value_generator
        CYBOX_SHORT_DESCRIPTION[definition.object_type] = definition.human_readable_type

    DBObservable.SUMMARY_BINDING = (
        ('type', original_get_obs_type),
        ('title', original_get_obs_title),
        ('description', original_get_obs_description),
        ('value', generate_custom_get_obs_value(custom_summary_value_map)),
    )

    WHICH_DBOBJ['obs'] = generate_db_observable_patch(custom_draft_handler_map)
