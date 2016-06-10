from itertools import chain

from stix.core.stix_package import STIXHeader, STIXPackage
from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.simple_marking import SimpleMarkingStructure
from stix.extensions.marking.terms_of_use_marking import TermsOfUseMarkingStructure
from stix.extensions.marking.tlp import TLPMarkingStructure

from edge import stixbase
from edge.generic import PACKAGE_ADD_DISPATCH, EdgeObject
from edge.handling import PackageXPath
from stix_extension.handling_marking import HandlingMarkingStructure


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
    handling = api_data["handling"][0]
    marking_structures = handling["marking_structures"]

    for structure in marking_structures:
        if structure['xsi:type'] == HandlingMarkingStructure._XSI_TYPE:
            handling_markings.append(structure)

    return handling_markings


def generate_stix_header(self):
    handling_markings = extract_handling_markings(self)
    stix_header = STIXHeader(
            handling=Marking([
                MarkingSpecification(
                        controlled_structure=PackageXPath.make_marking_xpath_by_node_relative(),
                        marking_structures=list(chain(
                                (TLPMarkingStructure(item) for item in [self.etlp] if item != 'NULL'),
                                (TermsOfUseMarkingStructure(item) for item in self.etou),
                                (SimpleMarkingStructure(item) for item in self.esms),
                                (HandlingMarkingStructure(item['caveat']) for item in handling_markings)
                        )),
                )
            ]),
    )
    return stix_header


def apply_patch():
    EdgeObject.capsulize = capsulize_patch
