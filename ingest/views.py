import csv
import re

from mongoengine import DoesNotExist
from mongoengine.connection import get_db
from datetime import datetime
from edge import IDManager
from edge.tools import StopWatch
from edge.inbox import InboxItem, InboxError
from edge.generic import ApiObject
from users.models import Draft, Repository_User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from adapters.certuk_mod.dedup.DedupInboxProcessor import DedupInboxProcessor
from adapters.certuk_mod.patch.incident_patch import DBIncidentPatch

REGEX_LINE_DELIMETER = re.compile("[\n]")
REGEX_BREAK_DELIMETER = re.compile("<br />")

TIME_KEY = ['Created', 'CustomField.{Containment Achieved}', 'CustomField.{First Data Exfiltration}',
            'CustomField.{First Malicious Action}', 'CustomField.{Incident Discovery}',
            'CustomField.{Incident Reported}',
            'CustomField.{Initial Compromise}', 'CustomField.{Restoration Achieved}', 'Resolved']

TIME_KEY_MAP = {'Created': 'incident_opened', 'CustomField.{Containment Achieved}': 'containment_achieved',
                'CustomField.{First Data Exfiltration}': 'first_data_exfiltration',
                'CustomField.{First Malicious Action}': 'first_malicious_action',
                'CustomField.{Incident Discovery}': 'incident_discovery',
                'CustomField.{Incident Reported}': 'incident_reported',
                'CustomField.{Initial Compromise}': 'initial_compromise',
                'CustomField.{Restoration Achieved}': 'restoration_achieved', 'Resolved': 'incident_closed'}


def remove_drafts(drafts):
    ids = []
    for draft in drafts:
        ids.append(draft['id'])
    db = get_db().drafts
    query = {'draft.id': {'$in': ids}}
    db.remove(query)


def create_time(data):
    time = {}
    for key in TIME_KEY:
        map_key = TIME_KEY_MAP[key]
        if data[key] != '':
            time_format = datetime.strptime(data[key], '%a %b %d %X %Y').isoformat()
            time[map_key] = {'precision': 'second', 'value': time_format}
    return time


def create_reporter(data):
    reporter = data['CustomField.{Reporter Type}']
    reporter_values = REGEX_BREAK_DELIMETER.split(reporter)
    new_reporter = ", ".join(reporter_values)
    return new_reporter


def create_intended_effects(data):
    joined_intended_effects = []
    intended_effects = data['CustomField.{Intended Effect}']
    intended_effects_values = REGEX_BREAK_DELIMETER.split(intended_effects)
    for effect in intended_effects_values:
        joined_intended_effects.append(effect)
    return joined_intended_effects


def status_checker(data):
    if data['Status'] == 'resolved':
        status = 'Closed'
    else:
        status = data['Status']
    return status


def initialise_draft(data):
    draft = {
        'attributed_actors': [],
        'categories': [data['CustomField.{Category}']],
        'description': '',
        'discovery_methods': [],
        'effects': [],
        'external_ids': [{'source': data['CustomField.{Indicator Data Files}'], 'id': ''}],
        'id': IDManager().get_new_id('incident'),
        'id_ns': IDManager().get_namespace(),
        'intended_effects': create_intended_effects(data),
        'leveraged_ttps': [],
        'related_incidents': [],
        'related_indicators': [],
        'related_observables': [],
        'reporter': {'identity': {'name': create_reporter(data),
                                  'specification': {'electronic_address_identifiers': [], 'free_text_lines': [],
                                                    'languages': [], 'party_name': {'name_lines': []}}}},
        'responders': [],
        'short_description': '',
        'status': status_checker(data),
        'title': 'RTIR ' + data['id'],
        'tlp': '',
        'trustgroups': [],
        'victims': [],
        'stixtype': 'inc',
        'time': create_time(data)
    }
    return draft


def create_drafts(request, elapsed):
    drafts, data = [], []
    raw_data = REGEX_LINE_DELIMETER.split(request.read())
    reader = csv.DictReader(raw_data)
    for row in reader:
        data.append(row)
    for incident in data:
        drafts.append(initialise_draft(incident))
    return drafts, data


@csrf_exempt
def ajax_create_incidents(request, username):

    if not request.method == 'POST':
        return JsonResponse({}, status=405)
    if not request.META.get('HTTP_ACCEPT') == 'application/json':
        return JsonResponse({}, status=406)
    if not request.META.get('CONTENT_TYPE') == 'text/csv':
        return JsonResponse({}, status=415)

    try:
        user = Repository_User.objects.get(username=username)
    except DoesNotExist:
        return JsonResponse({}, status=403)

    elapsed = StopWatch()
    try:
        drafts, data = [], []
        ip = DedupInboxProcessor(validate=False, user=user)
        raw_data = REGEX_LINE_DELIMETER.split(request.read())
        reader = csv.DictReader(raw_data)
        for row in reader:
            data.append(row)
        for incident in data:
            drafts.append(initialise_draft(incident))
        for draft in drafts:
            Draft.upsert('inc', draft, user)
            generic_object = ApiObject('inc', DBIncidentPatch.from_draft(draft))
            etlp, esms = 'NULL', ''
            ip.add(InboxItem(api_object=generic_object,
                             etlp=etlp,
                             esms=esms))
        ip.run()
        remove_drafts(drafts)
        return JsonResponse({
            'count': len(drafts),
            'duration': int(elapsed.ms()),
            'messages': ip.filter_messages,
            'state': 'success'
        }, status=202)
    except (KeyError, ValueError, InboxError) as e:
        validation_result = ip.validation_result if isinstance(ip, DedupInboxProcessor) else {}
        return JsonResponse({
            'count': len(drafts),
            'duration': int(elapsed.ms()),
            'messages': type(e).__name__ + ": " + e.message,
            'state': 'invalid',
            'validation_result': validation_result
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'duration': int(elapsed.ms()),
            'messages': [e.message],
            'state': 'error',
        }, status=500)
