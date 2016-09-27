
from indicator.observable_object_generator import ObservableObjectGenerator
from adapters.certuk_mod.builder import CUSTOM_OBSERVABLES


class CERTObservableObjectGenerator(ObservableObjectGenerator):

    def __init__(self):
        super(CERTObservableObjectGenerator, self).__init__()

    def _define_object_types(self):
        object_types = super(CERTObservableObjectGenerator, self)._define_object_types()
        object_types['File'].can_batch_create = True
        for definition in CUSTOM_OBSERVABLES:
            object_types[definition.human_readable_type] = definition.generate_observable_object_definition()
        return object_types
