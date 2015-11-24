
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
        self.builder_to_stix_object = kwargs['builder_to_stix_object']
        CustomObservableDefinition.__validate_function(self.builder_to_stix_object, 'builder_to_stix_object', 1)
        self.summary_value_generator = kwargs['summary_value_generator']
        CustomObservableDefinition.__validate_function(self.summary_value_generator, 'summary_value_generator', 1)
        self.to_draft_handler = kwargs['to_draft_handler']
        CustomObservableDefinition.__validate_function(self.to_draft_handler, 'to_draft_handler', 4)

    def generate_observable_object_definition(self):
        return ObservableObjectTypeDefinition(
            self.human_readable_type, self.can_batch_create, custom_id_prefix=self.custom_id_prefix,
            generator_function=self.builder_to_stix_object
        )

    @staticmethod
    def __validate_function(summary_value_generator, function_name, number_parameters):
        if not isinstance(number_parameters, int):
            raise TypeError('number_parameters must be an integer')
        if number_parameters < 0:
            raise ValueError('number_parameters must be >= 0')
        if not hasattr(summary_value_generator, '__call__'):
            raise TypeError('The supplied %s must be callable' % function_name)
        func_args = getargspec(summary_value_generator)
        if not (len(func_args[0]) == number_parameters or (len(func_args[0]) == (number_parameters + 1) and func_args[0][0] == 'self')):
            raise ValueError('The supplied %s must accept %i parameter(s) only' % (function_name, number_parameters))
