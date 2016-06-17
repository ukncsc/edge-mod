import csv
import sys
import pprint

from datetime import datetime
from edge import LOCAL_NAMESPACE

TIME_KEY = ['Created', 'CustomField.{Containment Achieved}', 'CustomField.{First Data Exfiltration}',
            'CustomField.{First Malicious Action}', 'CustomField.{Incident Discovery}',
            'CustomField.{Incident Reported}',
            'CustomField.{Initial Compromise}', 'CustomField.{Restoration Achieved}', 'Resolved']

TIME_KEY_MAP = {'Created': 'incident_discovery', 'CustomField.{Containment Achieved}': 'containment_achieved',
                'CustomField.{First Data Exfiltration}': 'first_data_exfiltration',
                'CustomField.{First Malicious Action}': 'first_malicious_action',
                'CustomField.{Incident Discovery}': 'incident_discovery',
                'CustomField.{Incident Reported}': 'incident_reported',
                'CustomField.{Initial Compromise}': 'initial_compromise',
                'CustomField.{Restoration Achieved}': 'restoration_achieved', 'Resolved': 'incident_closed'}

keys = ['id', 'status', 'created', 'category', 'containment achieved', 'external references', 'first data exfiltration',
        'first malicious action', 'incident discovery', 'incident reported', 'incident sector', 'indicator data files',
        'initial compromise', 'reporter type', 'resolution', 'restoration achieved']


def create_incident(data):
    drafts = create_drafts(data)
    return drafts


def create_time(data):
    time = {}
    for key in TIME_KEY:
        map_key = TIME_KEY_MAP[key]
        if data[key] != '':
            time_format = datetime.strptime(data[key], '%a %b %d %X %Y').isoformat()
            time[map_key] = {'precision': 'second', 'value': time_format}
    return time


def create_drafts(data):
    drafts = []
    for inc in data:
        draft = initialise_draft(inc)
        drafts.append(draft)
    return drafts


def initialise_draft(data):
    draft = {
        'attributed_actors': [],
        'categories': [data['CustomField.{Category}']],
        'description': '',
        'discovery_methods': [],
        'effects': [],
        'external_ids': {'source': '', 'id': data['CustomField.{Indicator Data Files}']},
        'id': '',
        'id_ns': '',
        'intended_effects': data['CustomField.{Intended Effect}'],
        'leveraged_ttps': [],
        'markings': '',
        'related_incidents': [],
        'related_indicators': [],
        'related_observables': [],
        'reporter': data['CustomField.{Reporter Type}'],
        'responders': [],
        'short_description': '',
        'status': data['Status'],
        'title': 'RTIR ' + data['id'],
        'tlp': '',
        'trustgroups': '',
        'victims': [],
        'stixtype': 'inc',
        'time': create_time(data)
    }
    return draft


def run():
    data = []
    with open('./Sample_data.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    drafts = create_drafts(data)
    pprint.PrettyPrinter(indent=4).pprint(drafts)
    print 'Amount of incidents = ' + str(len(drafts))
    print 'Length of keys  = ' + str(len(drafts[0]))


if __name__ == '__main__':
    run()
