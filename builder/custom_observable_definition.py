
from inspect import getargspec
from indicator.observable_object_type_definition import ObservableObjectTypeDefinition


class CustomObservableDefinition(object):

    def __init__(self, **kwargs):
        if self.__class__ == CustomObservableDefinition:
            raise AssertionError('CustomObservableDefintion base class should not be instantiated directly')
        super(CustomObservableDefinition, self).__init__()
        self.object_type = kwargs['object_type']
        self.human_readable_type = kwargs['human_readable_type']
        self.can_batch_create = kwargs.get('can_batch_create', False)
        self.custom_id_prefix = kwargs.get('custom_id_prefix', '')

    def generate_observable_object_definition(self):
        return ObservableObjectTypeDefinition(
            self.human_readable_type, self.can_batch_create, custom_id_prefix=self.custom_id_prefix,
            generator_function=self.builder_to_stix_object
        )

    def builder_to_stix_object(self, object_data):
        raise NotImplementedError('Must be overridden')

    def summary_value_generator(self, obj):
        raise NotImplementedError('Must be overridden')

    def to_draft_handler(self, observable, tg, load_by_id, id_ns=''):
        raise NotImplementedError('Must be overridden')
