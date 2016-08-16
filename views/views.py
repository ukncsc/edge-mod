import os
import urllib2
import urllib

import json
from datetime import datetime
from dateutil import tz
import mimetypes

from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied

from stix.extensions.marking.simple_marking import SimpleMarkingStructure

from users.decorators import superuser_or_staff_role, json_body
from users.models import Draft
from edge.generic import EdgeObject, load_edge_object_or_404
from edge.inbox import InboxProcessorForBuilders, InboxItem, InboxError
from edge import IDManager, NamespaceNotConfigured
from edge.handling import make_handling
from edge.tools import Optional
import rbac
from clippy.models import CLIPPY_TYPES

from adapters.certuk_mod.publisher.package_publisher import Publisher
from adapters.certuk_mod.publisher.publisher_config import PublisherConfig
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from adapters.certuk_mod.validation.builder.validator import BuilderValidationInfo
from adapters.certuk_mod.common.views import error_with_message

import adapters.certuk_mod.builder.customizations as cert_builder

from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.common.views import activity_log, ajax_activity_log
from adapters.certuk_mod.extract.views import extract_upload, extract_visualiser, extract_visualiser_get, \
    extract_visualiser_item_get, extract, extract_visualiser_merge_observables, extract_visualiser_delete_observables, \
    extract_visualiser_get_extended, delete_extract, extract_list, extract_status, uploaded_stix_extracts
from adapters.certuk_mod.common.logger import log_error, get_exception_stack_variable
from adapters.certuk_mod.cron import setup as cron_setup

from adapters.certuk_mod.cron.views import ajax_get_purge_task_status, ajax_run_purge
from adapters.certuk_mod.retention.views import ajax_get_retention_config, ajax_reset_retention_config, \
    ajax_set_retention_config

from adapters.certuk_mod.cron.views import ajax_get_fts_task_status, ajax_run_fts
from adapters.certuk_mod.fts.views import ajax_get_fts_config, ajax_reset_fts_config, \
    ajax_set_fts_config

from adapters.certuk_mod.dedup.views import duplicates_finder, ajax_load_duplicates, ajax_load_object, \
    ajax_load_parent_ids, ajax_import
from adapters.certuk_mod.config.views import ajax_get_crm_config, ajax_set_crm_config, ajax_get_cert_config, \
    ajax_get_sharing_groups, ajax_set_sharing_groups, ajax_get_markings, ajax_set_markings
from adapters.certuk_mod.audit import setup as audit_setup, status
from adapters.certuk_mod.audit.event import Event
from adapters.certuk_mod.audit.handlers import log_activity
from adapters.certuk_mod.audit.message import format_audit_message

from adapters.certuk_mod.common.objectid import discover as objectid_discover, find_id as objectid_find
from adapters.certuk_mod.catalog.backlink import BackLinkGenerator
from adapters.certuk_mod.catalog.duplicates import DuplicateFinder
from adapters.certuk_mod.catalog.edges import EdgeGenerator

from adapters.certuk_mod.retention.purge import STIXPurge

from adapters.certuk_mod.validation import FieldValidationInfo, ValidationStatus
from adapters.certuk_mod.visualiser.views import visualiser_discover, visualiser_not_found, visualiser_view, \
    visualiser_get, \
    visualiser_item_get, \
    visualiser_get_extended
from users.models import Repository_User

from adapters.certuk_mod.timeline.views import ajax_incident_timeline, timeline_discover, incident_timeline, \
    incident_timeline_not_found

audit_setup.configure_publisher_actions()
cert_builder.apply_customizations()
cron_setup.create_jobs()
mimetypes.init()
EDGE_DEPTH_LIMIT = 2
HANDLING_CAVEAT = 'HANDLING_CAVEAT'


@login_required
def static(request, path):
    clean_path = urllib2.unquote(path)
    if "../" not in clean_path:
        content_type, _ = mimetypes.guess_type(clean_path)
        return FileResponse(
                open(os.path.dirname(__file__) + "/../static/" + clean_path, mode="rb"),
                content_type=content_type
        )
    else:
        return HttpResponseNotFound()


@login_required
def discover(request):
    return objectid_discover(request, "publisher_review", "publisher_not_found")


TYPE_TO_URL = {
    'cam': 'campaign',
    'coa': 'course_of_action',
    'tgt': 'exploit_target',
    'inc': 'incident',
    'ind': 'indicator',
    'obs': 'observable',
    'act': 'threat_actor',
    'ttp': 'ttp'
}


@login_required
def clone(request):
    stix_id = objectid_find(request)
    try:
        if stix_id:
            edge_object = EdgeObject.load(stix_id)
            if edge_object.ty == 'obs':
                return error_with_message(request, "Observables cannot be cloned")
            new_id = IDManager().get_new_id(edge_object.ty)
            draft = edge_object.to_draft()
            draft['id'] = new_id
            Draft.upsert(edge_object.ty, draft, request.user)
            return redirect('/' + TYPE_TO_URL[edge_object.ty] + '/build/' + new_id, request)
        else:
            return error_with_message(request,
                                      "No clonable object found; please only choose " +
                                      "the clone option from an object's summary or external publish page")

    except Exception as e:
        ext_ref_error = "not found"
        if e.message.endswith(ext_ref_error):
            return error_with_message(request,
                                      "Unable to load object as some external references were not found: "
                                      + e.message[0:-len(ext_ref_error)])

        else:
            return error_with_message(request, e.message)


def _get_request_username(request):
    if hasattr(request, "user") and hasattr(request.user, "username"):
        return request.user.username
    return ""


def __extract_revision(id):
    revision = "latest"
    if '/' in id:
        revision = id.split('/')[1]
        id = id.split('/')[0]
    return revision, id


@login_required
def review(request, id):
    revision, id = __extract_revision(id)

    root_edge_object = PublisherEdgeObject.load(id, filters=request.user.filters(), revision=revision,
                                                include_revision_index=True)

    if revision is "latest":
        revision = root_edge_object.revisions[0]['timekey']

    package = PackageGenerator.build_package(root_edge_object)
    validation_info = PackageValidationInfo.validate(package)
    user_loader = lambda idref: EdgeObject.load(idref, request.user.filters())
    back_links = BackLinkGenerator.retrieve_back_links(root_edge_object, user_loader)
    edges = EdgeGenerator.gather_edges(root_edge_object.edges, depth_limit=EDGE_DEPTH_LIMIT, load_by_id=user_loader)

    req_user = _get_request_username(request)
    if root_edge_object.created_by_username != req_user:
        validation_info.validation_dict.update({id: {"created_by":
                                                         {"status": ValidationStatus.WARN,
                                                          "message": "This object was created by %s not %s"
                                                                     % (root_edge_object.created_by_username,
                                                                        req_user)}}})

    try:
        system_id_ns = IDManager().get_namespace()
    except NamespaceNotConfigured:
        system_id_ns = None

    created_by_organization = Optional(Repository_User).objects.get(
        id=root_edge_object.doc['created_by']).organization.value()
    can_revoke = (
        root_edge_object.id_ns == system_id_ns and
        request.user.organization is not None and
        created_by_organization == request.user.organization and
        root_edge_object.ty in ['ttp', 'cam', 'act', 'coa', 'tgt', 'inc', 'ind']
    )

    can_purge = can_revoke and root_edge_object.is_revoke()

    request.breadcrumbs([("Catalog", "")])
    return render(request, "catalog_review.html", {
        "root_id": id,
        "package": package,
        "trust_groups": json.dumps(root_edge_object.tg),
        "validation_info": validation_info,
        "kill_chain_phases": {item['phase_id']: item['name'] for item in KILL_CHAIN_PHASES},
        "back_links": json.dumps(back_links),
        "edges": json.dumps(edges),
        'view_url': '/' + CLIPPY_TYPES[root_edge_object.doc['type']].replace(' ', '_').lower() + (
        '/view/%s/' % urllib.quote(id)),
        'edit_url': '/' + CLIPPY_TYPES[root_edge_object.doc['type']].replace(' ', '_').lower() + (
        '/edit/%s/' % urllib.quote(id)),
        'visualiser_url': '/adapter/certuk_mod/visualiser/%s' % urllib.quote(id),
        'clone_url': "/adapter/certuk_mod/clone",
        "revisions": json.dumps(root_edge_object.revisions),
        "revision" : revision,
        'ajax_uri': reverse('catalog_ajax'),
        "can_revoke": can_revoke,
        "can_purge": can_purge
    })


@login_required
def object_details(request, id_):
    edge_obj = load_edge_object_or_404(id_)
    if not rbac.user_has_tlp_access(request.user, edge_obj):
        raise PermissionDenied

    return JsonResponse({
        'allow_edit': rbac.user_can_edit(request.user, edge_obj),
    })


@login_required
@json_body
def review_set_handling(request, data):
    try:
        edge_object = EdgeObject.load(data["rootId"])

        generic_object = edge_object.to_ApiObject()
        generic_object.obj.timestamp=datetime.now(tz.tzutc())
        append_handling(generic_object, data["handling"])
        ip = InboxProcessorForBuilders(
                user=request.user,
        )

        ip.add(InboxItem(api_object=generic_object, etlp=edge_object.etlp))
        ip.run()
        return {
            'messages': '',
            'success': True
        }
    except InboxError as e:
        log_activity(request.user, 'HANDLING', 'ERROR', e.message)
        log_error(e, 'adapters/dedup/import', 'Failed to set Handling')
        return JsonResponse({
            'messages': [e.message],
            'state': 'error'
        }, status=500)


def append_handling(edge_object, handling_markings):
    if getattr(edge_object.obj, "handling", None) is None:
        edge_object.obj.handling = make_handling(edge_object.ty)
    for handling in handling_markings:
        handling_caveat = SimpleMarkingStructure(handling)
        handling_caveat.marking_model_name = HANDLING_CAVEAT
        edge_object.obj.handling.markings[0].marking_structures.append(handling_caveat)


@login_required
def get_duplicates(request, id_):
    root_edge_object = PublisherEdgeObject.load(id_, filters=request.user.filters(), include_revision_index=True)
    duplicates = DuplicateFinder.find_duplicates(root_edge_object)

    return JsonResponse({"duplicates": duplicates})


@login_required
def not_found(request):
    return render(request, "publisher_not_found.html", {})


@login_required
@superuser_or_staff_role
def config(request):
    request.breadcrumbs([("CERT-UK Configuration", "")])
    return render(request, "config.html", {})


@login_required
@superuser_or_staff_role
@json_body
def ajax_get_sites(request, data):
    # The generic settings pages could define callbacks for dropdown options.
    # Probably just provide this data at the Django template rendering stage instead.
    # Or maybe make AJAX call optional, e.g. for large option lists?
    success = True
    error_message = ""
    sites = []

    try:
        sites = PublisherConfig.get_sites()
    except Exception, e:
        success = False
        error_message = e.message

    return {
        'success': success,
        'error_message': error_message,
        'sites': sites
    }


@login_required
@json_body
def ajax_get_datetime(request, data):
    configuration = settings.ACTIVE_CONFIG
    current_date_time = datetime.now(tz.gettz(configuration.by_key('display_timezone'))).strftime(
            '%Y-%m-%dT%H:%M:%S')
    return {'result': current_date_time}


@login_required
@superuser_or_staff_role
@json_body
def ajax_set_publish_site(request, data):
    success = True
    error_message = ''
    site_id = data.get('site_id', '')

    try:
        PublisherConfig.update_config(site_id)
    except Exception, e:
        success = False
        error_message = e.message
        site_id = ''

    return {
        'success': success,
        'saved_id': site_id,
        'error_message': error_message
    }


OnPublish = Event()
OnPublish.set_handler("Write to log", log_activity)


@login_required
@json_body
def ajax_publish(request, data):
    success = True
    error_message = ""
    root_id = None

    try:
        root_id = data['root_id']
        edge_object = PublisherEdgeObject.load(root_id)
        package = PackageGenerator.build_package(edge_object)
        namespace_info = edge_object.ns_dict()
        Publisher.push_package(package, namespace_info)
    # Narrow down which exceptions we catch...?
    except Exception, e:
        message = ''
        taxii_response = get_exception_stack_variable('tr')
        if taxii_response:
            message = '\nTAXII Staus Message:\n' + json.dumps(taxii_response.to_dict())
        log_error(e, 'Publisher', message)

        success = False
        error_message = e.message

    OnPublish.raise_event(ajax_publish, publish_status=status.PUBLISH_SUCCESS if success else status.PUBLISH_FAIL,
                          stix_id=root_id, user=request.user,
                          message=format_audit_message(error_message, data.get('publicationMessage')))

    # The whole try/except... return { success.. } thing seems repeated quite a bit for
    # our ajax handlers (and also in the core code)...
    return {
        'success': success,
        'error_message': error_message
    }


@login_required
@json_body
def ajax_validate(request, data):
    validation_info = {}
    success = True
    error_message = ''

    try:
        validation_info = BuilderValidationInfo.validate(data).validation_dict
    except Exception, e:
        success = False
        error_message = e.message

    return {
        'success': success,
        'error_message': error_message,
        'validation_info': validation_info
    }
