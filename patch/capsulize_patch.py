from itertools import chain

from stix.core.stix_package import STIXHeader, STIXPackage
from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.simple_marking import SimpleMarkingStructure
from stix.extensions.marking.terms_of_use_marking import TermsOfUseMarkingStructure
from stix.extensions.marking.tlp import TLPMarkingStructure

from edge import stixbase
from edge.generic import PACKAGE_ADD_DISPATCH, EdgeObject
from edge.handling import PackageXPath


def capsulize_patch(self, pkg_id, enable_bfs=False):
    contents = []
    pkg = STIXPackage(
            id_=pkg_id,
            stix_header=generate_stix_header(self)
    )

    if isinstance(self.obj, stixbase.DBStixBase):
        PACKAGE_ADD_DISPATCH[self.ty](pkg, self.obj._object)
    else:
        PACKAGE_ADD_DISPATCH[self.ty](pkg, self.obj)
    contents.append(self)

    if enable_bfs:
        from edge.scanner import STIXScanner
        for eo in STIXScanner({'_id': self.id_}, self.filters):
            if eo.id_ == self.id_: continue  # don't duplicate ourselves
            if isinstance(eo.obj, stixbase.DBStixBase):
                PACKAGE_ADD_DISPATCH[eo.ty](pkg, eo.obj._object)
            else:
                PACKAGE_ADD_DISPATCH[eo.ty](pkg, eo.obj)
            contents.append(eo)

    return pkg, contents


def extract_handling_markings(self):
    handling_markings = []
    api_data = self.apidata
    if 'handling' in api_data:
        handling = api_data["handling"][0]
        if 'marking_structures' in handling:
            marking_structures = handling["marking_structures"]

            for structure in marking_structures:
                if structure['xsi:type'] == SimpleMarkingStructure._XSI_TYPE:
                    handling_markings.append(structure)

    return handling_markings


def generate_stix_header(self):
    handling_markings = extract_handling_markings(self)
    stix_header = STIXHeader(
            handling=Marking([
                MarkingSpecification(
                        controlled_structure=PackageXPath.make_marking_xpath_by_node_relative(),
                        marking_structures=generate_marking_structure(self, handling_markings),
                )
            ]),
    )
    return stix_header


def generate_marking_structure(self, handling_markings):
    marking_structure = list(chain(
            (TLPMarkingStructure(item) for item in [self.etlp] if item != 'NULL'),
            (TermsOfUseMarkingStructure(item) for item in self.etou)),
    )

    marking_structure.extend(generate_simple_markings(handling_markings))

    return marking_structure


def generate_simple_markings(handling_markings):
    handling_list = list()
    for item in handling_markings:
        simple_structure = SimpleMarkingStructure(item['statement'])
        if not item.get("marking_model_name", None) is None:
            simple_structure.marking_model_name = item["marking_model_name"]
        handling_list.append(simple_structure)
    return handling_list


def apply_patch():
    EdgeObject.capsulize = capsulize_patch
