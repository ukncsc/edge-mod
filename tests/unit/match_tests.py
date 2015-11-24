
import unittest
from adapters.certuk_mod.tests.unit import view_loader
objectid_matcher = view_loader.get_views_module(__name__).objectid_matcher


class MatchTests(unittest.TestCase):

    def setUp(self):
        self.valid_id = '/PurpleSecureSystems:indicator-4a75d646-97e5-4002-9d24-038eacdaa06d/'
        self.empty_id = ''
        self.valid_mixed_case_id = '/PurpleSecureSystems:Indicator-4A75d646-97E5-4A02-9D24-038EACdaa06d/'
        self.non_hex_id = '/PurpleSecureSystems:indicator-4z75d646-97y5-4x02-9z24-038xacdaa06d/'
        self.alias_starts_With_non_az = '/-PurpleSecureSystems:indicator-4a75d646-97e5-4002-9d24-038eacdaa06d/'
        self.alias_contains_spaces = '/Purple Secure Systems:indicator-4a75d646-97e5-4002-9d24-038eacdaa06d/'
        self.characters_before_id = \
            'www.purplesecure.com/PurpleSecureSystems:indicator-4a75d646-97e5-4002-9d24-038eacdaa06d/'
        self.characters_after_id = \
            '/PurpleSecureSystems:indicator-4a75d646-97e5-4002-9d24-038eacdaa06d/some random string'
        self.empty_object_type = '/PurpleSecureSystems:-4a75d646-97e5-4002-9d24-038eacdaa06d/'
        self.non_az_object_type = '/PurpleSecureSystems:indicat0r-4a75d646-97e5-4002-9d24-038eacdaa06d/'

        self.regex_under_test = objectid_matcher

    def assertIsMatch(self, candidate_string):
        match = self.regex_under_test.match(candidate_string)
        self.assertIsNotNone(match)
        self.assertEqual(len(match.groups()), 1)

    def assertIsNotMatch(self, candidate_string):
        match = self.regex_under_test.match(candidate_string)
        self.assertIsNone(match)

    def test_IDMatch_Valid_Matches(self):
        self.assertIsMatch(self.valid_id)

    def test_IDMatch_Empty_Rejected(self):
        self.assertIsNotMatch(self.empty_id)

    def test_IDMatch_ValidMixedCase_Matches(self):
        self.assertIsMatch(self.valid_mixed_case_id)

    def test_IDMatch_NonHexID_Rejected(self):
        self.assertIsNotMatch(self.non_hex_id)

    def test_IDMatch_AliasStartsWithNonAZ_Rejected(self):
        self.assertIsNotMatch(self.alias_starts_With_non_az)

    def test_IDMatch_AliasContainsSpaces_Rejected(self):
        self.assertIsNotMatch(self.alias_contains_spaces)

    def test_IDMatch_CharactersBeforeID_Matches(self):
        self.assertIsMatch(self.characters_before_id)

    def test_IDMatch_CharactersAfterID_Rejected(self):
        self.assertIsNotMatch(self.characters_after_id)

    def test_IDMatch_EmptyObjectType_Rejected(self):
        self.assertIsNotMatch(self.empty_object_type)

    def test_IDMatch_NonAZObjectType_Rejected(self):
        self.assertIsNotMatch(self.empty_object_type)


if __name__ == '__main__':
    unittest.main()
