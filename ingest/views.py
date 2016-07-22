import csv
import re

from mongoengine import DoesNotExist
from mongoengine.connection import get_db
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
from adapters.certuk_mod.ingest.draft_from_rtir import initialise_draft

REGEX_LINE_DELIMETER = re.compile("[\n]")

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


def remove_drafts(drafts):
    ids = []
    for draft in drafts:
        ids.append(draft['id'])
    db = get_db().drafts
    query = {'draft.id': {'$in': ids}}
    db.remove(query)


def is_valid_request(request):
    if not request.method == 'POST':
        return False, 405
    if not request.META.get('HTTP_ACCEPT') == 'application/json':
        return False, 406
    if not request.META.get('CONTENT_TYPE') == 'text/csv':
        return False, 415
    else:
        return True, 200


def get_dict_reader(raw_data):
    reader = csv.DictReader(raw_data)
    reader.fieldnames = [key.strip() for key in reader.fieldnames]
    return reader


def draft_wrapper(data, drafts, drafts_validation):
    for incident in data:
        draft, draft_validation = initialise_draft(incident)
        if draft != {}:
            drafts.append(draft)
            drafts_validation.update(draft_validation)
    return drafts, drafts_validation


def upsert_drafts(ip, drafts, user):
    for draft in drafts:
        Draft.upsert('inc', draft, user)
        generic_object = ApiObject('inc', DBIncidentPatch.from_draft(draft))
        etlp, esms = 'NULL', ''
        ip.add(InboxItem(api_object=generic_object,
                         etlp=etlp,
                         esms=esms))
    return ip


def validate_csv_field_names(reader, ip):
    validation_result = {}
    for row in FIELDNAMES:
        if row not in reader.fieldnames:
            validation_result.setdefault('missing_columns', {}).update(
                {row: {'status': 'INFO', 'message': 'column not in csv file'}})
    return ip.validation_result.update(validation_result)


def build_validation_message(ip, drafts_validation, drafts, data):
    ids = []
    dropped_data = len(data) - len(drafts)
    if dropped_data:
        message = str(
            dropped_data) + ' incidents dropped as one of: (id, status, created timestamp, resolved timestamp) missing'
        ip.filter_messages.append(message)
    if ip.saved_count:
        for id_, eo in ip.contents.iteritems():
            validation_text = id_ + ' - ' + eo.api_object.obj.title
            ids.append(validation_text)
            if drafts_validation.get(id_):
                ip.validation_result.update({id_: drafts_validation[id_]})
    ip.filter_messages.extend(ids)
    return ip


def generate_error_message(username, message, e, elapsed):
    log_activity(username, 'INCIDENT INGEST', 'ERROR', message)
    log_error(e, 'adapters/incident/import', 'Import Failed')
    return JsonResponse({
        'duration': int(elapsed.ms()),
        'messages': [message],
        'state': 'error'
    }, status=500)


@csrf_exempt
def ajax_create_incidents(request, username):
    is_valid = is_valid_request(request)
    if is_valid[0] is False:
        return JsonResponse({}, status=is_valid[1])

    try:
        user = Repository_User.objects.get(username=username)
    except DoesNotExist:
        return JsonResponse({}, status=403)

    ip = None
    data, drafts, drafts_validation = [], [], {}
    elapsed = StopWatch()
    try:
        raw_data = REGEX_LINE_DELIMETER.split(request.read())
        reader = get_dict_reader(raw_data)
        data = [row for row in reader]
        drafts, drafts_validation = draft_wrapper(data, drafts, drafts_validation)

        ip = DedupInboxProcessor(validate=False, user=user)
        upsert_drafts(ip, drafts, user)
        ip.run()
        duration = int(elapsed.ms())
        remove_drafts(drafts), validate_csv_field_names(reader, ip), build_validation_message(ip, drafts_validation,
                                                                                              drafts, data)

        log_activity(username, 'INCIDENT INGEST', 'INFO', build_activity_message(
            ip.saved_count, duration, ip.filter_messages, ip.validation_result))
        return JsonResponse({
            'count': ip.saved_count,
            'duration': duration,
            'messages': ip.filter_messages,
            'state': 'success',
            'validation_result': ip.validation_result
        }, status=202)
    except (KeyError, ValueError, InboxError) as e:
        if drafts:  # Only have drafts if draft_wrapper has successfully executed
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
            return generate_error_message(username, 'Unable to parse file', e, elapsed)
        else:
            return generate_error_message(username, e.message, e, elapsed)
