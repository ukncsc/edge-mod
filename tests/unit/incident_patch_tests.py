import unittest
import mock
import edge
from adapters.certuk_mod.patch import incident_patch


class IncidentPatchTests(unittest.TestCase):
    coord_dict = {'identity': {
        'id': '123',
        'name': 'fred',
        'roles': [],
        'specification': {}
    }}

    draft_dict = {'categories': {u'Unauthorized Access'},
                  'time': {u'containment_achieved': {u'precision': 'second', u'value': u'2016-02-29T00:00:00+00:00'}},
                  'coordinators': [coord_dict],
                  'discovery_methods': ['Agent Disclosure'],
                  'intendend_effects' : ['Advantage']}

    @mock.patch.object(incident_patch.configuration, 'by_key')
    def test_AppendTimeZone(self, mock_config_method):
        mock_config_method.return_value = 'UTC'
        with_time_zone = {'value': u'2016-02-29T00:00:00+00:00'}
        with_time_zone2 = {'value': u'2016-02-29T00:00:00+00:00'}
        without_time_zone = {'value': u'2016-02-29T00:00:00'}

        # Test timezone appended
        incident_patch.DBIncidentPatch.append_timezone(without_time_zone)
        self.assertEqual(with_time_zone, without_time_zone)

        # Test no change
        incident_patch.DBIncidentPatch.append_timezone(with_time_zone)
        self.assertEqual(with_time_zone2, with_time_zone)

    @mock.patch.object(edge.incident.DBIncident, 'to_draft')
    def test_toDraft(self, mock_to_draft):
        mock_to_draft.return_value = {}

        class dummy_wrapped():
            @classmethod
            def __func__(cls, *args):
                return incident_patch.DBIncidentPatch()

        edge.incident.DBIncident.from_draft = incident_patch.from_draft_wrapper(dummy_wrapped)

        incident = incident_patch.DBIncidentPatch()
        incident = incident.from_draft(IncidentPatchTests.draft_dict)
        draft_return = incident.to_draft(incident, None, None);

        self.assertEqual(draft_return['time']['containment_achieved'], '2016-02-29T00:00:00+00:00');
        self.assertEqual(draft_return['categories'], ['Unauthorized Access']);
        self.assertEqual(draft_return['coordinators'], [IncidentPatchTests.coord_dict]);

    @mock.patch.object(edge.incident.DBIncident, 'update_with')
    def test_UpdateWith(self, mock_update_with):
        class dummy_wrapped():
            @classmethod
            def __func__(cls, *args):
                return incident_patch.DBIncidentPatch()

        edge.incident.DBIncident.from_draft = incident_patch.from_draft_wrapper(dummy_wrapped)

        incident = incident_patch.DBIncidentPatch()
        incident2 = incident_patch.DBIncidentPatch.from_draft(IncidentPatchTests.draft_dict)

        #Discovery methods & intended effects patched in update with to fix a soltra issue
        #as its not patched in from_draft and we mock out base from_draft, add in here
        incident2.discovery_methods.append('Agent Disclosure');
        incident2.intended_effects.append('Advantage');
        incident.update_with(incident2)

        self.assertEqual(incident.time.to_dict(), incident2.time.to_dict());
        self.assertEqual(incident.categories.to_dict(), incident2.categories.to_dict());
        self.assertEqual(incident.categories._inner.__len__(), 1);
        self.assertEqual(incident.coordinators.__len__(), 1);
        self.assertEqual(incident.discovery_methods.__len__(), 1);
        self.assertEqual(incident.intended_effects.__len__(), 1);
        self.assertEqual(str(incident.time._containment_achieved._value), u'2016-02-29 00:00:00+00:00');
