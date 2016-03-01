import unittest
import mock

from cybox.core import Observable, Object
from cybox.objects.file_object import File
from stix.indicator import Indicator

from edge.generic import ApiObject
from edge.inbox import InboxItem

from adapters.certuk_mod.dedup.DedupInboxProcessor import \
    _get_sighting_count,\
    _coalesce_duplicates,\
    _generate_message,\
    _is_matching_file


def create_file(file_name=None, md5=None, sha1=None, sha256=None):
    file_ = File()
    file_.file_name = file_name
    file_.md5 = md5
    file_.sha1 = sha1
    file_.sha256 = sha256
    api_object = ApiObject(ty='obs', apiobj=Observable(item=Object(file_)))
    api_object.api_object = api_object
    return api_object


class DedupInboxProcessorTests(unittest.TestCase):
    def test_get_sighting_count_not_set(self):
        obs = Observable()
        actual = _get_sighting_count(obs)
        self.assertEqual(actual, 1)

    def test_get_sighting_count_set_to_none(self):
        obs = Observable()
        obs.sighting_count = None
        actual = _get_sighting_count(obs)
        self.assertEqual(actual, 1)

    def test_get_sighting_count_set_to_one(self):
        obs = Observable()
        obs.sighting_count = 1
        actual = _get_sighting_count(obs)
        self.assertEqual(actual, 1)

    def test_get_sighting_count_set_to_two(self):
        obs = Observable()
        obs.sighting_count = 2
        actual = _get_sighting_count(obs)
        self.assertEqual(actual, 2)

    def test_coalesce_duplicates_to_sitings_empty_maptable(self):
        actual_out, actual_additional_sightings, actual_additional_file_hashes = _coalesce_duplicates({
            'pss:observable-00000000-0000-0000-0000-000000000001': mock.create_autospec(
                InboxItem, api_object=mock.create_autospec(
                    ApiObject, ty='obs', obj=mock.create_autospec(
                        Observable, id_='pss:observable-00000000-0000-0000-0000-000000000001', sighting_count=1
                    )
                ), etlp='WHITE')
        }, {})
        self.assertItemsEqual([
            'pss:observable-00000000-0000-0000-0000-000000000001'
        ], actual_out.keys())
        self.assertDictEqual({}, actual_additional_sightings)
        self.assertDictEqual({}, actual_additional_file_hashes)

    def test_coalesce_duplicates_to_sitings_with_maptable(self):
        actual_out, actual_additional_sightings, actual_additional_file_hashes = _coalesce_duplicates({
            'pss:observable-00000000-0000-0000-0000-000000000001': mock.create_autospec(
                InboxItem, api_object=mock.create_autospec(
                    ApiObject, ty='obs', obj=mock.create_autospec(
                        Observable, id_='pss:observable-00000000-0000-0000-0000-000000000001', sighting_count=1
                    )
                ), etlp='WHITE'),
            'pss:indicator-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                InboxItem, api_object=mock.create_autospec(
                    ApiObject, ty='ind', obj=mock.create_autospec(
                        Indicator, id_='pss:indicator-00000000-0000-0000-0000-000000000002'
                    )
                ), etlp='WHITE')
        }, {
            'pss:observable-00000000-0000-0000-0000-000000000001': 'pss:observable-11111111-1111-1111-1111-000000000001'
        })
        self.assertItemsEqual([
            'pss:indicator-00000000-0000-0000-0000-000000000002'
        ], actual_out.keys())
        self.assertDictEqual({
            'pss:observable-11111111-1111-1111-1111-000000000001': 1
        }, actual_additional_sightings)
        self.assertDictEqual({}, actual_additional_file_hashes)

    def test_generate_message_no_removals(self):
        self.assertEqual(_generate_message("Removed: %d", [1, 2], [1, 2]), None)

    def test_generate_message_one_removal(self):
        self.assertEqual(_generate_message("Removed: %d", [1, 2, 3], [1, 2]), 'Removed: 1')

    def test_is_matching_file_mismatch_filename(self):
        existing_file = create_file(file_name='file.1',
                                    md5='1bc29b36f623ba82aaf6724fd3b16718',
                                    sha1='415ab40ae9b7cc4e66d6769cb2c08106e8293b48',
                                    sha256='5d5b09f6dcb2d53a5fffc60c4ac0d55fabdf556069d6631545f42aa6e3500f2e')
        new_file = create_file(file_name='file.2',
                               md5='1bc29b36f623ba82aaf6724fd3b16718',
                               sha1='415ab40ae9b7cc4e66d6769cb2c08106e8293b48',
                               sha256='5d5b09f6dcb2d53a5fffc60c4ac0d55fabdf556069d6631545f42aa6e3500f2e')
        self.assertFalse(_is_matching_file(existing_file, new_file), "Shouldn't have matched")

    def test_is_matching_file_mismatch_md5(self):
        existing_file = create_file(file_name='file.1', md5='1bc29b36f623ba82aaf6724fd3b16718')
        new_file = create_file(file_name='file.1', md5='4e2dcf9208454aebce7ed56e93c67d78')
        self.assertFalse(_is_matching_file(existing_file, new_file), "Shouldn't have matched")

    def test_is_matching_file_mismatch_sha1(self):
        existing_file = create_file(file_name='file.1', sha1='415ab40ae9b7cc4e66d6769cb2c08106e8293b48')
        new_file = create_file(file_name='file.1', sha1='3e65819230df66ec6f55427a242a2ff11c7d7884')
        self.assertFalse(_is_matching_file(existing_file, new_file), "Shouldn't have matched")

    def test_is_matching_file_mismatch_sha256(self):
        existing_file = create_file(file_name='file.1', sha256='5d5b09f6dcb2d53a5fffc60c4ac0d55fabdf556069d6631545f42aa6e3500f2e')
        new_file = create_file(file_name='file.1', sha256='f1375dbd646b47651d1a5f9e4c0868c61bd622d65e35e1f5f4c7e3afb00e47b5')
        self.assertFalse(_is_matching_file(existing_file, new_file), "Shouldn't have matched")

    def test_is_matching_file_match_md5(self):
        existing_file = create_file(file_name='file.1', md5='1bc29b36f623ba82aaf6724fd3b16718')
        new_file = create_file(file_name='file.1', md5='1bc29b36f623ba82aaf6724fd3b16718')
        self.assertTrue(_is_matching_file(existing_file, new_file), "Should have matched")

    def test_is_matching_file_match_sha1(self):
        existing_file = create_file(file_name='file.1', sha1='415ab40ae9b7cc4e66d6769cb2c08106e8293b48')
        new_file = create_file(file_name='file.1', sha1='415ab40ae9b7cc4e66d6769cb2c08106e8293b48')
        self.assertTrue(_is_matching_file(existing_file, new_file), "Should have matched")

    def test_is_matching_file_match_sha256(self):
        existing_file = create_file(file_name='file.1', sha256='5d5b09f6dcb2d53a5fffc60c4ac0d55fabdf556069d6631545f42aa6e3500f2e')
        new_file = create_file(file_name='file.1', sha256='5d5b09f6dcb2d53a5fffc60c4ac0d55fabdf556069d6631545f42aa6e3500f2e')
        self.assertTrue(_is_matching_file(existing_file, new_file), "Should have matched")
