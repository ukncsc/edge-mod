import sys
from stix.bindings import *
import stix.bindings.data_marking as data_marking_binding

XML_NS = "http://data-marking.mitre.org/extensions/MarkingStructure#Handling-1"


#
# Data representation classes.
#

class HandlingMarkingStructureType(data_marking_binding.MarkingStructureType):
    """The HandlingMarkingStructureType is a basic implementation of the data
    marking schema that allows for a string statement to be
    associated with the data being marked. This is to be used for how the data is handled"""
    subclass = None
    superclass = data_marking_binding.MarkingStructureType

    def __init__(self, marking_model_ref=None, marking_model_name=None, caveat=None):
        super(HandlingMarkingStructureType, self).__init__(marking_model_ref=marking_model_ref,
                                                         marking_model_name=marking_model_name)
        self.xmlns = XML_NS
        self.xmlns_prefix = "handlingMarking"
        self.xml_type = "HandlingMarkingStructureType"
        self.caveat = caveat

    def factory(*args_, **kwargs_):
        if HandlingMarkingStructureType.subclass:
            return HandlingMarkingStructureType.subclass(*args_, **kwargs_)
        else:
            return HandlingMarkingStructureType(*args_, **kwargs_)

    factory = staticmethod(factory)

    def get_caveat(self):
        return self.caveat

    def set_caveat(self, caveat):
        self.caveat = caveat

    def hasContent_(self):
        if (
            self.caveat is not None or
            super(HandlingMarkingStructureType, self).hasContent_()
            ):
            return True
        else:
            return False

    def export(self, lwrite, level, nsmap, namespace_=XML_NS, name_='HandlingMarkingStructureType', namespacedef_='',
               pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        showIndent(lwrite, level, pretty_print)
        lwrite('<%s:%s%s' % (nsmap[namespace_], name_, namespacedef_ and ' ' + namespacedef_ or '',))
        already_processed = set()
        self.exportAttributes(lwrite, level, already_processed, namespace_, name_='HandlingMarkingStructureType')
        if self.hasContent_():
            lwrite('>%s' % (eol_,))
            self.exportChildren(lwrite, level + 1, nsmap, XML_NS, name_, pretty_print=pretty_print)
            showIndent(lwrite, level, pretty_print)
            lwrite('</%s:%s>%s' % (nsmap[namespace_], name_, eol_))
        else:
            lwrite('/>%s' % (eol_,))

    def exportAttributes(self, lwrite, level, already_processed, namespace_='handlingMarking:',
                         name_='HandlingMarkingStructureType'):
        super(HandlingMarkingStructureType, self).exportAttributes(lwrite, level, already_processed, namespace_,
                                                                 name_='HandlingMarkingStructureType')
        # if 'xmlns' not in already_processed:
        #     already_processed.add('xmlns')
        #     xmlns = " xmlns:%s='%s'" % (self.xmlns_prefix, self.xmlns)
        #     lwrite(xmlns)
        if 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            xsi_type = " xsi:type='%s:%s'" % (self.xmlns_prefix, self.xml_type)
            lwrite(xsi_type)

    def exportChildren(self, lwrite, level, nsmap, namespace_=XML_NS, name_='HandlingMarkingStructureType',
                       fromsubclass_=False, pretty_print=True):
        super(HandlingMarkingStructureType, self).exportChildren(lwrite, level, nsmap, namespace_, name_, True,
                                                               pretty_print=pretty_print)
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.caveat is not None:
            showIndent(lwrite, level, pretty_print)
            lwrite('<%s:Caveat>%s</%s:Caveat>%s' % (
            nsmap[namespace_], quote_xml(self.caveat), nsmap[namespace_], eol_))

    def build(self, node):
        already_processed = set()
        self.buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, node, nodeName_)

    def buildAttributes(self, node, attrs, already_processed):
        super(HandlingMarkingStructureType, self).buildAttributes(node, attrs, already_processed)

    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        if nodeName_ == 'caveat':
            caveat_ = child_.text
            caveat_ = self.gds_validate_string(caveat_, node, 'caveat')
            self.caveat = caveat_
        super(HandlingMarkingStructureType, self).buildChildren(child_, node, nodeName_, True)


# end class HandlingMarkingStructureType

GDSClassesMapping = {}

USAGE_TEXT = """
Usage: python <Parser>.py [ -s ] <in_xml_file>
"""


def usage():
    print USAGE_TEXT
    sys.exit(1)


def get_root_tag(node):
    tag = Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = GDSClassesMapping.get(tag)
    if rootClass is None:
        rootClass = globals().get(tag)
    return tag, rootClass


def parse(inFileName):
    doc = parsexml_(inFileName)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HandlingMarkingStructureType'
        rootClass = HandlingMarkingStructureType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    # sys.stdout.write('<?xml version="1.0" ?>\n')
    # rootObj.export(sys.stdout, 0, name_=rootTag,
    #     namespacedef_='',
    #     pretty_print=True)
    return rootObj


def parseEtree(inFileName):
    doc = parsexml_(inFileName)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HandlingMarkingStructureType'
        rootClass = HandlingMarkingStructureType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    rootElement = rootObj.to_etree(None, name_=rootTag)
    content = etree_.tostring(rootElement, pretty_print=True,
                              xml_declaration=True, encoding="utf-8")
    sys.stdout.write(content)
    sys.stdout.write('\n')
    return rootObj, rootElement


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HandlingMarkingStructureType'
        rootClass = HandlingMarkingStructureType
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    # sys.stdout.write('<?xml version="1.0" ?>\n')
    # rootObj.export(sys.stdout, 0, name_="HandlingMarkingStructureType",
    #     namespacedef_='')
    return rootObj


def main():
    args = sys.argv[1:]
    if len(args) == 1:
        parse(args[0])
    else:
        usage()


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    main()

__all__ = [
    "HandlingMarkingStructureType"
]
