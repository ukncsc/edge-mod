
import unittest


class MatchTests(unittest.TestCase):

    def test_IDMatch_Valid_Matches(self):
        self.assertEqual(True, False)

    def test_IDMatch_Empty_Rejected(self):
        pass

    def test_IDMatch_ValidMixedCase_Matches(self):
        pass

    def test_IDMatch_NonHexID_Rejected(self):
        pass

    def test_IDMatch_AliasStartsWithNonAZ_Rejected(self):
        pass

    def test_IDMatch_CharactersBeforeID_Matches(self):
        pass

    def test_IDMatch_CharactersAfterID_Matches(self):
        pass

    def test_IDMatch_ZeroLengthObjectType_Rejected(self):
        pass


if __name__ == '__main__':
    unittest.main()
