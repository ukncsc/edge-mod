import mock
import unittest

from adapters.certuk_mod.ingest.draft_from_rtir import create_time, create_generic_values, \
    create_external_ids, status_checker, initialise_draft


class IncidentIngestTests(unittest.TestCase):
    def setUp(self):
        self.draft = {
            'categories': '',
            'description': '',
            'external_ids': [],
            'id': 'pss:inc-00000001-0001-0001-0001-00000001',
            'id_ns': 'http://www.purplesecure.com',
            'intended_effects': '',
            'reporter': {'identity': {'name': ''}},
            'status': 'Closed',
            'title': 'RTIR 1500',
            'victims': [{'name': '', 'specification': {'organisation_info': {'industry_type': 'Water'}}}],
            'stixtype': 'inc',
            'time': {}
        }

    def test_no_time(self):
        data = {'Created': '',
                'CustomField.{Containment Achieved}': '',
                'CustomField.{First Data Exfiltration}': '',
                'CustomField.{First Malicious Action}': '',
                'CustomField.{Incident Discovery}': '',
                'CustomField.{Incident Reported}': '',
                'CustomField.{Initial Compromise}': '',
                'CustomField.{Restoration Achieved}': '',
                'Resolved': ''}
        time = create_time(data)
        self.assertEqual(time, {})

    def test_with_time(self):
        data = {'Created': '',
                'CustomField.{Containment Achieved}': 'Sun Oct 05 00:00:00 2014',
                'CustomField.{First Data Exfiltration}': 'Wed Oct 01 00:00:00 2014',
                'CustomField.{First Malicious Action}': 'Tue Sep 30 00:00:00 2014',
                'CustomField.{Incident Discovery}': '',
                'CustomField.{Incident Reported}': '',
                'CustomField.{Initial Compromise}': '',
                'CustomField.{Restoration Achieved}': '',
                'Resolved': ''}
        time = create_time(data)
        compare_time = {'containment_achieved': {'precision': 'second',
                                                 'value': '2014-10-05T00:00:00'},
                        'first_data_exfiltration': {'precision': 'second',
                                                    'value': '2014-10-01T00:00:00'},
                        'first_malicious_action': {'precision': 'second',
                                                   'value': '2014-09-30T00:00:00'}}
        self.assertDictEqual(time, compare_time)

    def test_generic_values_without_join(self):
        data = {'CustomField.{Intended Effect}': 'Fraud<br />Brand Damage<br />Advantage - Economic'}
        generic_values = create_generic_values(data, 'CustomField.{Intended Effect}', False)
        compare_effects = ['Fraud', 'Brand Damage', 'Advantage - Economic']
        self.assertListEqual(generic_values, compare_effects)

    def test_generic_values_without_join_no_values(self):
        data = {'CustomField.{Intended Effect}': ''}
        generic_values = create_generic_values(data, 'CustomField.{Intended Effect}', False)
        self.assertListEqual(generic_values, [''])

    def test_generic_values_with_join(self):
        data = {'CustomField.{Reporter Type}': 'Domestic Source<br />Government Agency'}
        generic_values = create_generic_values(data, 'CustomField.{Reporter Type}', True)
        self.assertEquals(generic_values, 'Domestic Source, Government Agency')

    def test_generic_values_with_join_no_values(self):
        data = {'CustomField.{Reporter Type}': ''}
        generic_values = create_generic_values(data, 'CustomField.{Reporter Type}', True)
        self.assertEquals(generic_values, '')

    def test_no_status(self):
        data = {'Status': ''}
        status = status_checker(data)
        compare_status = ''
        self.assertEquals(status, compare_status)

    def test_status_resolved(self):
        data = {'Status': 'resolved'}
        status = status_checker(data)
        compare_status = 'Closed'
        self.assertEquals(status, compare_status)

    def test_status_not_resolved(self):
        data = {'Status': 'New'}
        status = status_checker(data)
        compare_status = 'New'
        self.assertEquals(status, compare_status)

    def test_reporter_type(self):
        data = {'CustomField.{Reporter Type}': 'Domestic Source<br />Government Agency'}
        reporter = create_generic_values(data, 'CustomField.{Reporter Type}', True)
        compare_reporter = 'Domestic Source, Government Agency'
        self.assertEquals(reporter, compare_reporter)

    @mock.patch('adapters.certuk_mod.ingest.draft_from_rtir.IDManager')
    def test_validation_for_draft(self, mock_manager):
        data = {
            'id': '1500',
            'CustomField.{Indicator Data Files}': '14007indicator536.csv',
            'Created': 'value',
            'CustomField.{Containment Achieved}': 'value',
            'CustomField.{First Data Exfiltration}': 'value',
            'CustomField.{First Malicious Action}': 'value',
            'CustomField.{Incident Discovery}': 'value',
            'CustomField.{Incident Reported}': 'value',
            'CustomField.{Initial Compromise}': 'value',
            'CustomField.{Restoration Achieved}': 'value',
            'CustomField.{Description}': 'value',
            'CustomField.{Category}': 'value',
            'CustomField.{Reporter Type}': 'value',
            'CustomField.{Incident Sector}': 'Water',
            'Status': '',
            'CustomField.{Intended Effect}': 'value',
            'Resolved': 'value'
        }
        mock_manager().get_new_id.return_value = 'pss:inc-00000001-0001-0001-0001-00000001'
        draft_validation = initialise_draft(data)[1]
        validation_result = {'pss:inc-00000001-0001-0001-0001-00000001': {
            'status': {'status': 'INFO', 'message': 'no value provided for status'}}}
        self.assertDictEqual(draft_validation, validation_result)

    @mock.patch('adapters.certuk_mod.ingest.draft_from_rtir.IDManager')
    def test_no_validation_for_draft(self, mock_manager):
        data = {
            'id': '1500',
            'CustomField.{Indicator Data Files}': '14007indicator536.csv',
            'Created': 'value',
            'CustomField.{Containment Achieved}': 'value',
            'CustomField.{First Data Exfiltration}': 'value',
            'CustomField.{First Malicious Action}': 'value',
            'CustomField.{Incident Discovery}': 'value',
            'CustomField.{Incident Reported}': 'value',
            'CustomField.{Initial Compromise}': 'value',
            'CustomField.{Restoration Achieved}': 'value',
            'CustomField.{Description}': 'value',
            'CustomField.{Category}': 'value',
            'CustomField.{Reporter Type}': 'value',
            'CustomField.{Incident Sector}': 'Water',
            'Status': 'value',
            'CustomField.{Intended Effect}': 'value',
            'Resolved': 'value'
        }
        mock_manager().get_new_id.return_value = 'pss:inc-00000001-0001-0001-0001-00000001'
        draft_validation = initialise_draft(data)[1]
        validation_result = {}
        self.assertDictEqual(draft_validation, validation_result)

    @mock.patch('adapters.certuk_mod.ingest.draft_from_rtir.IDManager')
    @mock.patch('adapters.certuk_mod.ingest.draft_from_rtir.create_time')
    @mock.patch('adapters.certuk_mod.ingest.draft_from_rtir.create_generic_values')
    @mock.patch('adapters.certuk_mod.ingest.draft_from_rtir.create_external_ids')
    @mock.patch('adapters.certuk_mod.ingest.draft_from_rtir.status_checker')
    def test_initialise_draft(self, mock_status, mock_external_ids, mock_generic_values, mock_time, mock_manager):
        mock_status.return_value = 'Closed'
        mock_external_ids.return_value = []
        mock_generic_values.return_value = ''
        mock_time.return_value = {}
        mock_manager().get_namespace.return_value = 'http://www.purplesecure.com'
        mock_manager().get_new_id.return_value = 'pss:inc-00000001-0001-0001-0001-00000001'
        data = {
            'id': '1500',
            'CustomField.{Indicator Data Files}': '14007indicator536.csv',
            'Created': '',
            'CustomField.{Containment Achieved}': '',
            'CustomField.{First Data Exfiltration}': '',
            'CustomField.{First Malicious Action}': '',
            'CustomField.{Incident Discovery}': '',
            'CustomField.{Incident Reported}': '',
            'CustomField.{Initial Compromise}': '',
            'CustomField.{Restoration Achieved}': '',
            'CustomField.{Description}': '',
            'CustomField.{Category}': '',
            'CustomField.{Reporter Type}': '',
            'CustomField.{Incident Sector}': 'Water',
            'Status': '',
            'CustomField.{Intended Effect}': '',
            'Resolved': ''
        }
        draft = initialise_draft(data)[0]
        mock_status.assert_called_with(data)
        mock_external_ids.assert_called_with(data)
        mock_time.assert_called_with(data)
        self.assertDictEqual(draft, self.draft)
