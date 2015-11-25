from clippy.models import CLIPPY_TYPES
from edge import LOCAL_ALIAS
from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus, ObjectValidationInfo


class NamespaceValidationInfo(ObjectValidationInfo):

    def __init__(self, **field_validation):
        super(NamespaceValidationInfo, self).__init__(**field_validation)
        self.namespace = field_validation.get(r'namespace')

    @classmethod
    def validate(cls, type_, id_):
        field_validation = {}
        if not NamespaceValidationInfo.__id_is_current_ns(id_):
            field_validation[r'namespace'] = FieldValidationInfo(
                ValidationStatus.WARN,
                r'%s originates from an external namespace' % CLIPPY_TYPES.get(type_, r'Object')
            )
        return cls(**field_validation)

    @staticmethod
    def __id_is_current_ns(id_):
        ns_prefix = LOCAL_ALIAS + r':'
        return str(id_).startswith(ns_prefix)

    def is_local(self):
        return self.namespace is None
