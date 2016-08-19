from stix.extensions.identity.ciq_identity_3_0 import STIXCIQIdentity3_0, OrganisationInfo, PartyName, Language, \
    Address, ElectronicAddressIdentifier, FreeTextLine, ContactNumber


class STIXCIQIdentity3_0patch(STIXCIQIdentity3_0):

    def to_dict(self):
        d = {}
        if self.party_name:
            d['party_name'] = self.party_name.to_dict()
        if self.languages:
            d['languages'] = [x.to_dict() for x in self.languages]
        if self.addresses:
            d['addresses'] = [x.to_dict() for x in self.addresses]
        if self.electronic_address_identifiers:
            d['electronic_address_identifiers'] = [x.to_dict() for x in self.electronic_address_identifiers]
        if self.free_text_lines:
            d['free_text_lines'] = [x.to_dict() for x in self.free_text_lines]
        if self.contact_numbers:
            d['contact_numbers'] = [x.to_dict() for x in self.contact_numbers]
        if self.organisation_info:
            d['organisation_info'] = self.organisation_info.to_dict()

        return d

    @classmethod
    def from_dict(cls, dict_repr, return_obj=None):
        if not dict_repr:
            return None

        if not return_obj:
            return_obj = cls()

        return_obj.party_name = PartyName.from_dict(dict_repr.get('party_name'))
        return_obj.languages = [Language.from_dict(x) for x in dict_repr.get('languages', [])]
        return_obj.addresses = [Address.from_dict(x) for x in dict_repr.get('addresses', [])]
        return_obj.electronic_address_identifiers = [ElectronicAddressIdentifier.from_dict(x) for x in
                                                     dict_repr.get('electronic_address_identifiers', [])]
        return_obj.free_text_lines = [FreeTextLine.from_dict(x) for x in dict_repr.get('free_text_lines', [])]
        return_obj.contact_numbers = [ContactNumber.from_dict(x) for x in dict_repr.get('contact_numbers', [])]
        return_obj.organisation_info = OrganisationInfo.from_dict(dict_repr.get('organisation_info'))

        return return_obj


def apply_patch():
    STIXCIQIdentity3_0.to_dict = STIXCIQIdentity3_0patch().to_dict
    STIXCIQIdentity3_0.from_dict = STIXCIQIdentity3_0patch.from_dict
