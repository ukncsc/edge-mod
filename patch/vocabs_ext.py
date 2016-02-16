# extension of stix vocabs for CIQ_3.0
#from http://stix.mitre.org/language/version1.1.1/xsddocs/XMLSchema/extensions/identity/ciq_3.0/1.1.1/xPIL_xsd.html#ElectronicAddressIdentifiers_ElectronicAddressIdentifiers_ElectronicAddressIdentifier_Type
# the XSD defines an enumeration that python-stix does not enforce.

from stix.common import vocabs


class ElectronicAddressIdentifierType(vocabs.VocabString):
    _namespace = 'http://stix.mitre.org/default_vocabularies-1'
    _XSI_TYPE = 'stixVocabs:ElectronicAddressIdentifierTypeVocab-1.1.1'
    _ALLOWED_VALUES = (
        'AIM',
        'EMAIL',
        'GOOGLE',
        'GIZMO',
        'ICQ',
        'JABBER',
        'MSN',
        'SIP',
        'SKYPE',
        'URL',
        'XRI',
        'YAHOO'
    )
    TERM_AIM = "AIM"
    TERM_EMAIL = "EMAIL"
    TERM_GOOGLE = "GOOGLE"
    TERM_GIZMO = "GIZMO"
    TERM_ICQ = "ICQ"
    TERM_JABBER = "JABBER"
    TERM_MSN = "MSN"
    TERM_SIP = "SIP"
    TERM_SKYPE = "SKYPE"
    TERM_URL = "URL"
    TERM_XRI = "XRI"
    TERM_YAHOO = "YAHOO"
