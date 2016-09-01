import os
import urllib
import json
from datetime import datetime
from dateutil import tz
import rbac

from django.http import HttpResponse, Http404
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from stix.extensions.marking.simple_marking import SimpleMarkingStructure

from crashlog.models import save
from clippy.models import CLIPPY_TYPES
from users.decorators import json_body

from edge.generic import EdgeError
from edge.generic import EdgeObject, load_edge_object_or_404
from edge.inbox import InboxProcessorForBuilders, InboxItem, InboxError
from edge.handling import make_handling
from edge.sightings import getSightingsFollowHash

from adapters.certuk_mod.catalog.generate_snort import generate_snort
from adapters.certuk_mod.common.logger import log_error
from adapters.certuk_mod.publisher.package_generator import PackageGenerator
from adapters.certuk_mod.publisher.publisher_edge_object import PublisherEdgeObject
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.catalog.backlink import BackLinkGenerator
from adapters.certuk_mod.catalog.duplicates import DuplicateFinder
from adapters.certuk_mod.catalog.edges import EdgeGenerator
from adapters.certuk_mod.catalog.revoke import Revocable
from adapters.certuk_mod.validation import ValidationStatus

EDGE_DEPTH_LIMIT = 1
HANDLING_CAVEAT = 'HANDLING_CAVEAT'


def __extract_revision(id):
    revision = "latest"
    if '/' in id:
        revision = id.split('/')[1]
        id = id.split('/')[0]
    return revision, id


def _get_request_username(request):
    if hasattr(request, "user") and hasattr(request.user, "username"):
        return request.user.username
    return ""


@login_required
def review(request, id):
    revision, id = __extract_revision(id)

    root_edge_object = PublisherEdgeObject.load(id, filters=request.user.filters(), revision=revision,
                                                include_revision_index=True)

    if revision is "latest":
        revision = root_edge_object.revisions[0]['timekey']

    package = PackageGenerator.build_package(root_edge_object)
    validation_info = PackageValidationInfo.validate(package)

    def user_loader(idref):
        return EdgeObject.load(idref, request.user.filters())

    back_links = BackLinkGenerator.retrieve_back_links(root_edge_object, user_loader)
    edges = EdgeGenerator.gather_edges(root_edge_object.edges, depth_limit=EDGE_DEPTH_LIMIT, load_by_id=user_loader)

    sightings = None
    if root_edge_object.ty == 'obs':
        sightings = getSightingsFollowHash(root_edge_object.doc['data']['hash'])

    req_user = _get_request_username(request)
    if root_edge_object.created_by_username != req_user:
        validation_info.validation_dict.update({id: {"created_by":
                                                         {"status": ValidationStatus.WARN,
                                                          "message": "This object was created by %s not %s"
                                                                     % (root_edge_object.created_by_username,
                                                                        req_user)}}})

    revocable = Revocable(root_edge_object, request)
    can_revoke = revocable.is_revocable()
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
        'clone_url': "/adapter/certuk_mod/clone_direct/" + id,
        "revisions": json.dumps(root_edge_object.revisions),
        "revision": revision,
        "version": root_edge_object.version,
        "sightings": sightings,
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
        generic_object.obj.timestamp = datetime.now(tz.tzutc())
        append_handling(generic_object, data["handling"])
        ip = InboxProcessorForBuilders(
            user=request.user,
        )

        ip.add(InboxItem(api_object=generic_object, etlp=edge_object.etlp))
        ip.run()
        return {
            'message': '',
            'state': 'success',
            "success": True
        }
    except InboxError as e:
        log_error(e, 'adapters/review/handling', 'Failed to set Handling')
        return {
            'message': e.message,
            'state': 'error',
            "success": False
        }


def append_handling(edge_object, handling_markings):
    if getattr(edge_object.obj, "handling", None) is None:
        edge_object.obj.handling = make_handling(edge_object.ty)
    for handling in handling_markings:
        handling_caveat = SimpleMarkingStructure(handling)
        handling_caveat.marking_model_name = HANDLING_CAVEAT
        edge_object.obj.handling.markings[0].marking_structures.append(handling_caveat)


@login_required
def get_duplicates(request, id_):
    root_edge_object = PublisherEdgeObject.load(id_, filters=request.user.filters())
    duplicates = DuplicateFinder.find_duplicates(root_edge_object)

    return JsonResponse({"duplicates": duplicates})


@login_required
def observable_extract(request, type, obs_type, id_, revision):

    def text_writer(value, obs_type_in):
        if obs_type_in == obs_type or obs_type == "all":
            return value + os.linesep
        return ""

    def snort_writer(value, obs_type_in):
        if obs_type_in == obs_type or obs_type == "all":
            snort_val = generate_snort(value, obs_type_in, id_.split(':', 1)[1].split('-', 1)[1])
            if snort_val:
                return snort_val + os.linesep
        return ""

    def not_implemented_writer(value, obs_type_in):
        return ""

    result = ""
    if type == "text":
        writer = text_writer
    elif type == "SNORT":
        writer = snort_writer
    else:
        writer = not_implemented_writer
        result = "%s not implemented" % type

    stack = [id_]
    history = set()
    while stack:
        node_id = stack.pop()

        if node_id in history:
            continue
        history.add(node_id)

        try:
            eo = EdgeObject.load(node_id, request.user.filters(), revision=revision if node_id is id_ else "latest")
        except EdgeError:
            continue

        for edge in eo.edges:
            stack.append(edge.id_)

        if eo.ty != 'obs':
            continue

        if eo.apidata.has_key("observable_composition"):
            continue

        result += writer(eo.summary['value'], eo.summary['type'])

    response = HttpResponse(content_type='text/txt')
    response['Content-Disposition'] = 'attachment; filename="%s_%s_%s.txt"' % (type, obs_type, id_)
    response.write(result)
    return response
