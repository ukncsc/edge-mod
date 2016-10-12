from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus, ObjectValidationInfo
from edge.generic import EdgeObject, EdgeError

class CommonValidationInfo(ObjectValidationInfo):

    TLP_MAP = {'RED': 4, 'AMBER': 3, 'GREEN': 2, 'WHITE': 1, 'NULL': 0}

    def __init__(self, **field_validation):
        super(CommonValidationInfo, self).__init__(**field_validation)
        self.tlp = field_validation.get(r'tlp')

    @classmethod
    def validate(cls, **common_data):

        item = common_data.get(r'item')
        if not item:
            item = common_data

        item_tlp = item.get(r'tlp')

        package_dict = common_data.get(r'package_dict')

        if package_dict:
            package_tlp = package_dict.get(r'tlp')
        else:
            package_dict = {}
            package_tlp = None

        field_validation = {}

        if not package_tlp:
            try:
                package_tlp = package_dict['handling'][0]['marking_structures'][0]['color']
            except LookupError:
                package_tlp = 'NULL'

        if not item_tlp:
            try:
                item_tlp = item['handling'][0]['marking_structures'][0]['color']
            except LookupError:
                try:
                    eo = EdgeObject.load(item['id'])
                    item_tlp = eo.etlp if hasattr(eo, 'etlp') else 'NULL'
                except EdgeError:
                    item_tlp = package_tlp

        if not item_tlp or item_tlp == 'NULL':
            field_validation[r'tlp'] = FieldValidationInfo(ValidationStatus.ERROR, r'TLP missing')
        elif cls.TLP_MAP[item_tlp] > cls.TLP_MAP[package_tlp]:
            field_validation[r'tlp'] = FieldValidationInfo(ValidationStatus.WARN,
                                                           r'Child object has less permissive TLP')

        return cls(**field_validation)