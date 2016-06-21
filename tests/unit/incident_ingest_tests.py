import mock
import unittest

from adapters.certuk_mod.ingest.views import create_time, create_drafts, create_reporter, \
    create_intended_effects, status_checker


class IncidentIngestTests(unittest.TestCase):
    def setUp(self):
        self.draft = {
            'attributed_actors': [],
            'categories': [],
            'description': '',
            'discovery_methods': [],
            'effects': [],
            'external_ids': [],
            'id': 'pss:matt',
            'id_ns': 'http://www.purplescure.com',
            'intended_effects': [],
            'leveraged_ttps': [],
            'related_incidents': [],
            'related_indicators': [],
            'related_observables': [],
            'reporter': {'identity': {'name': '',
                                      'specification': {'electronic_address_identifiers': [], 'free_text_lines': [],
                                                        'languages': [], 'party_name': {'name_lines': []}}}},
            'responders': [],
            'short_description': '',
            'status': '',
            'title': '',
            'tlp': '',
            'trustgroups': [],
            'victims': [],
            'stixtype': 'inc',
            'time': {}
        }

    def test_create_time(self):

        pass
