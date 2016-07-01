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
from adapters.certuk_mod.dedup.views import build_activity_message
from adapters.certuk_mod.patch.incident_patch import DBIncidentPatch
from adapters.certuk_mod.common.activity import save as log_activity
from adapters.certuk_mod.common.logger import log_error

REGEX_LINE_DELIMETER = re.compile("[\n]")
REGEX_BREAK_DELIMETER = re.compile("<br />")


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
    for key, _map in TIME_KEY_MAP.iteritems():
        if data.get(key, '') != '':
            time_format = datetime.strptime(data.get(key, ''), '%a %b %d %X %Y').isoformat()
            time[_map] = {'precision': 'second', 'value': time_format}
    return time


def create_reporter(data):
    reporter = data.get('CustomField.{Reporter Type}', '')
    reporter_values = REGEX_BREAK_DELIMETER.split(reporter)
    new_reporter = ", ".join(reporter_values)
    return new_reporter


def create_intended_effects(data):
    joined_intended_effects = []
    intended_effects = data.get('CustomField.{Intended Effect}', '')
    intended_effects_values = REGEX_BREAK_DELIMETER.split(intended_effects)
    for effect in intended_effects_values:
        joined_intended_effects.append(effect)
    return joined_intended_effects


def status_checker(data):
    if data.get('Status', '') == 'resolved':
        status = 'Closed'
    else:
        status = data.get('Status')
    return status


def initialise_draft(data):
    draft = {
        'attributed_actors': [],
        'categories': [data.get('CustomField.{Category}', '')],
        'description': '',
        'discovery_methods': [],
        'effects': [],
        'external_ids': [{'source': data.get('CustomField.{External References}', ''), 'id': data.get('CustomField.{Indicator Data Files}', '')}],
        'id': IDManager().get_new_id('incident'),
        'id_ns': IDManager().get_namespace(),
        'intended_effects': create_intended_effects(data),
        'leveraged_ttps': [],
        'related_incidents': [],
        'related_indicators': [],
        'related_observables': [],
        'reporter': {'name': create_reporter(data), 'specification': {'organisation_info': {'industry_type': ''}}},
        'responders': [],
        'short_description': '',
        'status': status_checker(data),
        'title': 'RTIR ' + data.get('id', ''),
        'tlp': '',
        'trustgroups': [],
        'victims': [{'name': '',
                     'specification': {'organisation_info': {'industry_type': data.get('CustomField.{Incident Sector}', '')}}}],
        'stixtype': 'inc',
        'time': create_time(data)
    }
    return draft


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

    ip = None
    drafts, data = [], []
    elapsed = StopWatch()
    try:
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
        duration = int(elapsed.ms())
        remove_drafts(drafts)
        if len(ip.filter_messages) == 0 and ip.message:
            ip.filter_messages.append(ip.message)
        log_activity(username, 'INCIDENT INGEST', 'INFO', build_activity_message(
            ip.saved_count, duration, ip.filter_messages, ip.validation_result))
        return JsonResponse({
            'count': ip.saved_count,
            'duration': duration,
            'messages': ip.filter_messages,
            'state': 'success'
        }, status=202)
    except (KeyError, ValueError, InboxError) as e:
        if drafts:
            remove_drafts(drafts)
        count = ip.saved_count if isinstance(ip, DedupInboxProcessor) else 0
        duration = int(elapsed.ms())
        messages = [e.message]
        validation_result = ip.validation_result if isinstance(ip, DedupInboxProcessor) else {}
        log_activity(username, 'INCIDENT INGEST', 'WARN', build_activity_message(
            count, duration, messages, validation_result
        ))
        return JsonResponse({
            'count': count,
            'duration': duration,
            'messages': messages,
            'state': 'invalid',
            'validation_result': validation_result
        }, status=400)
    except Exception as e:
        if e.message == 'line contains NULL byte':
            log_activity(username, 'INCIDENT INGEST', 'ERROR', 'Unable to parse file')
            log_error(e, 'adapters/incident/import', 'Import failed')
            return JsonResponse({
                'duration': int(elapsed.ms()),
                'messages': ['Unable to parse file'],
                'state': 'error'
            }, status=500)
        else:
            log_activity(username, 'INCIDENT INGEST', 'ERROR', e.message)
            log_error(e, 'adapters/incident/import', 'Import failed')
            return JsonResponse({
                'duration': int(elapsed.ms()),
                'messages': [e.message],
                'state': 'error'
            }, status=500)
