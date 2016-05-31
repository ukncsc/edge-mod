import unittest
import mock

from cybox.core import Observable, Object
from cybox.objects.file_object import File
from stix.indicator import Indicator
from stix.ttp import TTP, Behavior
from stix.ttp.attack_pattern import AttackPattern
from stix.exploit_target import ExploitTarget
from stix.exploit_target.vulnerability import Vulnerability
from stix.common.structured_text import StructuredText

from edge.generic import ApiObject
from edge.inbox import InboxItem
from edge import LOCAL_NAMESPACE

from adapters.certuk_mod.dedup.DedupInboxProcessor import \
    _get_sighting_count,\
    _coalesce_duplicates,\
    _generate_message,\
    _is_matching_file, \
    _coalesce_non_observable_duplicates, \
    _package_title_capec_string_to_ids, \
    _package_cve_id_to_ids, \
    _get_map_table

EXTERNAL_NAMESPACE = "Matt's Namespace"
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

    def test_coalesce_ttps_with_no_maptable(self):
        contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp')),
                    'pss:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp'))}

        coalesce = _coalesce_non_observable_duplicates(contents, {})

        self.assertItemsEqual(['pss:ttp-00000000-0000-0000-0000-000000000001',
                               'pss:ttp-00000000-0000-0000-0000-000000000002'], coalesce.keys())

    def test_coalesce_ttps_with_maptable(self):
        contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp')),
                    'pss:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp'))}

        coalesce = _coalesce_non_observable_duplicates(contents, {'pss:ttp-00000000-0000-0000-0000-000000000002': 'DeDuptoMe'})

        self.assertItemsEqual(['pss:ttp-00000000-0000-0000-0000-000000000001'], coalesce.keys())

    def test_package_ttps_to_consider_not_matching_only_external_ns(self):
        contents = {'matt:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'matt:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP, title='Shouldn\'t match', id_ns = EXTERNAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')])))),
                    'matt:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'matt:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = EXTERNAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')]))))}

        package_ttps_local = _package_title_capec_string_to_ids(contents, True)
        package_ttps_external = _package_title_capec_string_to_ids(contents, False)

        self.assertDictEqual({}, package_ttps_local)
        self.assertDictEqual({'shouldn\'t match: CAPEC-163': ['matt:ttp-00000000-0000-0000-0000-000000000001'],
                              'should match: CAPEC-163': ['matt:ttp-00000000-0000-0000-0000-000000000002']},
                             package_ttps_external)

    def test_package_ttps_to_consider_not_matching_only_local_ns(self):
        contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP, title='Shouldn\'t match', id_ns = LOCAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')])))),
                    'pss:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = LOCAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')]))))}

        package_ttps_local = _package_title_capec_string_to_ids(contents, True)
        package_ttps_external = _package_title_capec_string_to_ids(contents, False)

        self.assertDictEqual({'shouldn\'t match: CAPEC-163': ['pss:ttp-00000000-0000-0000-0000-000000000001'],
                              'should match: CAPEC-163': ['pss:ttp-00000000-0000-0000-0000-000000000002']},
                             package_ttps_local)
        self.assertDictEqual({}, package_ttps_external)

    def test_package_ttps_to_consider_local_and_external_ns(self):
        contents = {'matt:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP, title='Should match', id_ns = EXTERNAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')])))),
                    'pss:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = LOCAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')]))))}

        package_ttps_local = _package_title_capec_string_to_ids(contents, True)
        package_ttps_non_local = _package_title_capec_string_to_ids(contents, False)

        self.assertDictEqual({'should match: CAPEC-163':
                                  ['pss:ttp-00000000-0000-0000-0000-000000000002']}, package_ttps_local)
        self.assertDictEqual({'should match: CAPEC-163':
                                  ['matt:ttp-00000000-0000-0000-0000-000000000001']}, package_ttps_non_local)

    def test_package_ttps_to_consider_matching_only_external_ns(self):
        contents = {'matt:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'matt:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP, title='Should match', id_ns = EXTERNAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')])))),
                    'matt:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'matt:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = EXTERNAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')]))))}

        package_ttps_local = _package_title_capec_string_to_ids(contents, True)
        package_ttps_external = _package_title_capec_string_to_ids(contents, False)

        self.assertDictEqual({}, package_ttps_local)
        self.assertDictEqual({'should match: CAPEC-163': [
            'matt:ttp-00000000-0000-0000-0000-000000000001', 'matt:ttp-00000000-0000-0000-0000-000000000002'
        ]}, package_ttps_external)

    def test_package_ttps_to_consider_matching_only_local_ns(self):
        contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP, title='Should match', id_ns = LOCAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')])))),
                    'pss:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = LOCAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-163')]))))}

        package_ttps_local = _package_title_capec_string_to_ids(contents, True)
        package_ttps_external = _package_title_capec_string_to_ids(contents, False)

        self.assertDictEqual({'should match: CAPEC-163': [
            'pss:ttp-00000000-0000-0000-0000-000000000001', 'pss:ttp-00000000-0000-0000-0000-000000000002'
        ]}, package_ttps_local)
        self.assertDictEqual({}, package_ttps_external)

    def test_package_ttps_to_consider_matching_local_and_external_ns(self):
        contents = {'pss:ind-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ind-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ind')),
                    'External:ttp-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'External:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = EXTERNAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-1'),
                                           mock.create_autospec(AttackPattern, capec_id = 'CAPEC-2')])))),
                    'External:ttp-00000000-0000-0000-0000-000000000003': mock.create_autospec(
                        InboxItem, id= 'External:ttp-00000000-0000-0000-0000-000000000003',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = EXTERNAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-1'),
                                           mock.create_autospec(AttackPattern, capec_id = 'CAPEC-2')])))),
                    'pss:ttp-00000000-0000-0000-0000-000000000003': mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000003',
                        api_object = mock.create_autospec(ApiObject, ty='ttp',
                        obj = mock.create_autospec(TTP,  title='Should match', id_ns = LOCAL_NAMESPACE,
                        behavior = mock.create_autospec(Behavior,
                        attack_patterns = [mock.create_autospec(AttackPattern, capec_id = 'CAPEC-1'),
                                           mock.create_autospec(AttackPattern, capec_id = 'CAPEC-2'),
                                           mock.create_autospec(AttackPattern, capec_id = 'CAPEC-3')]))))
                    }

        package_ttps_local = _package_title_capec_string_to_ids(contents, True)
        package_ttps_external = _package_title_capec_string_to_ids(contents, False)

        self.assertDictEqual({'should match: CAPEC-1,CAPEC-2,CAPEC-3':
                                  ['pss:ttp-00000000-0000-0000-0000-000000000003']}, package_ttps_local)
        self.assertDictEqual({'should match: CAPEC-1,CAPEC-2':
                              ['External:ttp-00000000-0000-0000-0000-000000000003',
                               'External:ttp-00000000-0000-0000-0000-000000000002']}, package_ttps_external)

    def test_package_tgts_to_consider_not_matching_only_external_ns(self):
        contents = {'matt:tgt-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = EXTERNAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')]))),
                    'matt:tgt-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = EXTERNAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1112')])))}

        package_tgts_local = _package_cve_id_to_ids(contents, True)
        package_tgts_external = _package_cve_id_to_ids(contents, False)

        self.assertDictEqual({}, package_tgts_local)
        self.assertDictEqual({'CVE-2015-1111': ['matt:tgt-00000000-0000-0000-0000-000000000001'],
                             'CVE-2015-1112': ['matt:tgt-00000000-0000-0000-0000-000000000002']}, package_tgts_external)

    def test_package_tgts_to_consider_not_matching_only_local_ns(self):
        contents = {'pss:tgt-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = LOCAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')]))),
                    'pss:tgt-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = LOCAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1112')])))}

        package_tgts_local = _package_cve_id_to_ids(contents, True)
        package_tgts_external = _package_cve_id_to_ids(contents, False)

        self.assertDictEqual({'CVE-2015-1111': ['pss:tgt-00000000-0000-0000-0000-000000000001'],
                             'CVE-2015-1112': ['pss:tgt-00000000-0000-0000-0000-000000000002']}, package_tgts_local)
        self.assertDictEqual({}, package_tgts_external)

    def test_package_tgts_to_consider_not_matching_local_and_external_ns(self):
        contents = {'matt:tgt-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = EXTERNAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')]))),
                    'pss:tgt-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = LOCAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1112')])))}

        package_tgts_local = _package_cve_id_to_ids(contents, True)
        package_tgts_external = _package_cve_id_to_ids(contents, False)

        self.assertDictEqual({'CVE-2015-1112': ['pss:tgt-00000000-0000-0000-0000-000000000002']}
                             ,package_tgts_local)
        self.assertDictEqual({'CVE-2015-1111': ['matt:tgt-00000000-0000-0000-0000-000000000001']}
                             ,package_tgts_external)

    def test_package_tgts_to_consider_matching_only_external_ns(self):
        contents = {'matt:tgt-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = EXTERNAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')]))),
                    'matt:tgt-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = EXTERNAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')])))}

        package_tgts_local = _package_cve_id_to_ids(contents, True)
        package_tgts_external = _package_cve_id_to_ids(contents, False)

        self.assertDictEqual({}, package_tgts_local)
        self.assertDictEqual({'CVE-2015-1111': ['matt:tgt-00000000-0000-0000-0000-000000000002',
                                                'matt:tgt-00000000-0000-0000-0000-000000000001']}
                             ,package_tgts_external)

    def test_package_tgts_to_consider_matching_only_local_ns(self):
        contents = {'pss:tgt-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:tgt-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = LOCAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')]))),
                    'pss:tgt-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'pss:tgt-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = LOCAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')])))}

        package_tgts_local = _package_cve_id_to_ids(contents, True)
        package_tgts_external = _package_cve_id_to_ids(contents, False)

        self.assertDictEqual({'CVE-2015-1111': ['pss:tgt-00000000-0000-0000-0000-000000000002',
                                                'pss:tgt-00000000-0000-0000-0000-000000000001']}
                             ,package_tgts_local)
        self.assertDictEqual({}, package_tgts_external)

    def test_package_tgts_to_consider_matching_local_and_external_ns(self):
        contents = {'pss:tgt-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:tgt-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = LOCAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')]))),
                    'pss:tgt-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'pss:tgt-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = LOCAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2015-1111')]))),
                    'matt:tgt-00000000-0000-0000-0000-000000000001': mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = EXTERNAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2016-1111')]))),
                    'matt:tgt-00000000-0000-0000-0000-000000000002': mock.create_autospec(
                        InboxItem, id= 'matt:tgt-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='tgt',
                        obj = mock.create_autospec(ExploitTarget, id_ns = EXTERNAL_NAMESPACE,
                        vulnerabilities = [mock.create_autospec(Vulnerability, cve_id = 'CVE-2016-1112')])))}

        package_tgts_local = _package_cve_id_to_ids(contents, True)
        package_tgts_external = _package_cve_id_to_ids(contents, False)

        self.assertDictEqual({'CVE-2015-1111': ['pss:tgt-00000000-0000-0000-0000-000000000002',
                                                'pss:tgt-00000000-0000-0000-0000-000000000001']}
                             ,package_tgts_local)
        self.assertDictEqual({'CVE-2016-1111': ['matt:tgt-00000000-0000-0000-0000-000000000001'],
                              'CVE-2016-1112': ['matt:tgt-00000000-0000-0000-0000-000000000002']
                              }, package_tgts_external)

    def test_map_table_duplicates(self):
        contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'Short')))),
                    'pss:ttp-00000000-0000-0000-0000-000000000002':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'Longerr'))))}
        key_to_ids = {'key1': ['pss:ttp-00000000-0000-0000-0000-000000000001',
                               'pss:ttp-00000000-0000-0000-0000-000000000002']}

        map_table = _get_map_table(contents, key_to_ids)

        self.assertDictEqual({'pss:ttp-00000000-0000-0000-0000-000000000001': 'pss:ttp-00000000-0000-0000-0000-000000000002'},
                             map_table)

    def test_map_table_no_duplicates(self):
        contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'short')))),
                    'pss:ttp-00000000-0000-0000-0000-000000000002':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'longer'))))}
        key_to_ids = {}

        map_table = _get_map_table(contents, key_to_ids)
        self.assertDictEqual({}, map_table)

    def test_map_table_no_duplicates_2(self):
        contents = contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'short')))),
                    'pss:ttp-00000000-0000-0000-0000-000000000002':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'longer')))),
                    'pss:ttp-00000000-0000-0000-0000-000000000003':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000003',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'even longer'))))}

        key_to_ids = {'key1': ['pss:ttp-00000000-0000-0000-0000-000000000001'],
                      'key2':['pss:ttp-00000000-0000-0000-0000-000000000002'],
                      'key3': ['pss:ttp-00000000-0000-0000-0000-000000000003']}
        map_table = _get_map_table(contents, key_to_ids)

        self.assertDictEqual({},map_table)

    def test_map_table_3_duplicates(self):
        contents = {'pss:ttp-00000000-0000-0000-0000-000000000001':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000001',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'short')))),
                    'pss:ttp-00000000-0000-0000-0000-000000000002':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000002',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'longer')))),
                    'pss:ttp-00000000-0000-0000-0000-000000000003':mock.create_autospec(
                        InboxItem, id= 'pss:ttp-00000000-0000-0000-0000-000000000003',
                        api_object = mock.create_autospec(ApiObject, ty='ttp', obj = mock.create_autospec(
                            ExploitTarget, description = mock.create_autospec(StructuredText, value = 'even longer'))))}

        key_to_ids = {'key1': ['pss:ttp-00000000-0000-0000-0000-000000000001', 'pss:ttp-00000000-0000-0000-0000-000000000002',
                               'pss:ttp-00000000-0000-0000-0000-000000000003']}

        map_table = _get_map_table(contents, key_to_ids)

        self.assertDictEqual({'pss:ttp-00000000-0000-0000-0000-000000000001': 'pss:ttp-00000000-0000-0000-0000-000000000003',
                              'pss:ttp-00000000-0000-0000-0000-000000000002': 'pss:ttp-00000000-0000-0000-0000-000000000003'},
                             map_table)
