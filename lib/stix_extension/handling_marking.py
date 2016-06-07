import stix_extension.bindings.handling_marking as handling_marking_binding
import stix.data_marking
from stix.data_marking import MarkingStructure


class HandlingMarkingStructure(MarkingStructure):
    _binding = handling_marking_binding
    _binding_class = handling_marking_binding.HandlingMarkingStructureType
    _namespace = 'http://data-marking.mitre.org/extensions/MarkingStructure#Handling-1'
    _XSI_TYPE = "handlingMarking:HandlingMarkingStructureType"

    def __init__(self, caveat=None):
        super(HandlingMarkingStructure, self).__init__()
        self.caveat = caveat

    def to_obj(self, return_obj=None, ns_info=None):
        super(HandlingMarkingStructure, self).to_obj(return_obj=return_obj, ns_info=ns_info)

        obj = self._binding_class()

        MarkingStructure.to_obj(self, return_obj=obj, ns_info=ns_info)

        obj.caveat = self.caveat

        return obj

    def to_dict(self):
        d = MarkingStructure.to_dict(self)
        if self.caveat:
            d['caveat'] = self.caveat

        return d

    @staticmethod
    def from_obj(obj):
        if not obj:
            return None

        m = HandlingMarkingStructure()
        MarkingStructure.from_obj(obj, m)
        m.caveat = obj.caveat

        return m

    @staticmethod
    def from_dict(marking_dict):
        if not marking_dict:
            return None

        m = HandlingMarkingStructure()
        MarkingStructure.from_dict(marking_dict, m)
        m.caveat = marking_dict.get('caveat')

        return m


stix.data_marking.add_extension(HandlingMarkingStructure)

