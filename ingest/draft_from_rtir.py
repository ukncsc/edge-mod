import re

from dateutil.parser import parse
from edge import IDManager

REGEX_BREAK_DELIMETER = re.compile("<br />")

TIME_KEY_MAP = {'Created': 'incident_opened', 'CustomField.{Containment Achieved}': 'containment_achieved',
                'CustomField.{First Data Exfiltration}': 'first_data_exfiltration',
                'CustomField.{First Malicious Action}': 'first_malicious_action',
                'CustomField.{Incident Discovery}': 'incident_discovery',
                'CustomField.{Incident Reported}': 'incident_reported',
                'CustomField.{Initial Compromise}': 'initial_compromise',
                'CustomField.{Restoration Achieved}': 'restoration_achieved', 'Resolved': 'incident_closed'}

FIELDNAMES = {'id': 'title', 'CustomField.{Indicator Data Files}': 'external_id', 'Created': 'created',
              'CustomField.{Containment Achieved}': 'containment_achieved',
              'CustomField.{First Data Exfiltration}': 'first_data_exfiltration',
              'CustomField.{First Malicious Action}': 'first_malicious_action',
              'CustomField.{Incident Discovery}': 'incident_discovery',
              'CustomField.{Incident Reported}': 'incident_reported',
              'CustomField.{Initial Compromise}': 'initial_compromise',
              'CustomField.{Restoration Achieved}': 'restoration_achieved', 'CustomField.{Description}': 'description',
              'CustomField.{Category}': 'categories',
              'CustomField.{Reporter Type}': 'reporter_type', 'CustomField.{Incident Sector}': 'incident_sector',
              'Status': 'status', 'CustomField.{Intended Effect}': 'intended_effects',
              'Resolved': 'resolved'}

ESSENTIAL_FIELDS = ['id', 'created', 'status']


def initialise_draft(data):
    if data.get('id', '') == '' or data.get('Created', '') == '' or data.get('Status', '') == '':
        return {}, {}

    draft = {
        'categories': create_generic_values(data, 'CustomField.{Category}', False),
        'description': data.get('CustomField.{Description}', ''),
        'external_ids': create_external_ids(data),
        'id': IDManager().get_new_id('incident'),
        'id_ns': IDManager().get_namespace(),
        'intended_effects': create_generic_values(data, 'CustomField.{Intended Effect}', False),
        'reporter': {'identity': {'name': create_generic_values(data, 'CustomField.{Reporter Type}', True)}},
        'status': status_checker(data),
        'title': 'RTIR ' + data.get('id', ''),
        'victims': [{'name': '',
                     'specification': {
                         'organisation_info': {'industry_type': data.get('CustomField.{Incident Sector}', '')}}}],
        'stixtype': 'inc',
        'time': create_time(data)
    }
    validation_for_draft = {}
    for field, name in FIELDNAMES.iteritems():
        if data.get(field, '') == '':
            validation_for_draft.setdefault(draft['id'], {}).update(
                {name: {'status': 'INFO', 'message': 'no value provided for ' + name}})
    return draft, validation_for_draft


def create_generic_values(data, field, join):
    value = data.get(field, '')
    split_values = REGEX_BREAK_DELIMETER.split(value)
    split_values_clean = [sv.strip() for sv in split_values]
    if join:
        return ", ".join(split_values_clean)
    else:
        return split_values_clean


def create_time(data):
    time = {}
    for key, _map in TIME_KEY_MAP.iteritems():
        if data.get(key, '') != '':
            try:
                time_format = parse(data.get(key,'')).isoformat()
                time[_map] = {'precision': 'second', 'value': time_format}
            except Exception as e:
                print e.message
    return time


def create_external_ids(data):
    external_id = []
    if data.get('CustomField.{Indicator Data Files}') != '':
        external_id.append({
            'source': '',
            'id': data.get('CustomField.{Indicator Data Files}', '')
        })
    return external_id


def status_checker(data):
    if data.get('Status') == 'resolved':
        status = 'Closed'
    else:
        status = data.get('Status')
    return status
