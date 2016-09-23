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
from adapters.certuk_mod.patch.incident_patch import DBIncidentPatch

HANDLING_CAVEAT = "HANDLING_CAVEAT"


def _get_request_username(request):
    if hasattr(request, "user") and hasattr(request.user, "username"):
        return request.user.username
    return ""


def generate_partial_review_data(request, id, revision):
    root_edge_object = PublisherEdgeObject.load(id, filters=request.user.filters(), revision=revision,
                                                include_revision_index=True)
    package = PackageGenerator.build_package(root_edge_object)
    validation_info = PackageValidationInfo.validate(package)

    def user_loader(idref):
        return EdgeObject.load(idref, request.user.filters())

    edges = EdgeGenerator.gather_edges(root_edge_object.edges, load_by_id=user_loader)

    req_user = _get_request_username(request)
    if root_edge_object.created_by_username != req_user:
        validation_info.validation_dict.update({id: {"created_by":
                                                         {"status": ValidationStatus.WARN,
                                                          "message": "This object was created by %s not %s"
                                                                     % (root_edge_object.created_by_username,
                                                                        req_user)}}})
    if any(item['is_external'] for item in edges):
        validation_info.validation_dict.update({id: {"external_references":
                                                         {"status": ValidationStatus.ERROR,
                                                          "message": "This object contains External References, clone "
                                                                     "object and remove missing references before publishing"}}})

    # add root object to edges for javascript to construct object
    edges.append({
        'ty': root_edge_object.ty,
        'id_': root_edge_object.id_,
        'is_external': False
    })

    return {
        'root_edge_object': root_edge_object,
        'package': package,
        "trust_groups": root_edge_object.tg,
        "validation_info": validation_info,
        "edges": edges,
        "revision": root_edge_object.version
    }


@login_required
@json_body
def reload_data(request, data):
    review_data = generate_partial_review_data(request, data["id"], data["revision"])

    return {
        'package': review_data["package"].to_dict(),
        "trust_groups": json.dumps(review_data["trust_groups"]),
        "validation_info": review_data["validation_info"].to_json(),
        "edges": review_data["edges"],
        "revision": review_data["revision"]
    }


@login_required
def review(request, id):
    data = generate_partial_review_data(request, id, 'latest')

    root_edge_object = data["root_edge_object"]

    def user_loader(idref):
        return EdgeObject.load(idref, request.user.filters())

    back_links = BackLinkGenerator.retrieve_back_links(root_edge_object, user_loader)

    sightings = None
    if root_edge_object.ty == 'obs':
        sightings = getSightingsFollowHash(root_edge_object.doc['data']['hash'])

    revision = root_edge_object.revisions[0]['timekey']

    revocable = Revocable(root_edge_object, request)

    can_revoke = revocable.is_revocable()

    can_purge = can_revoke and root_edge_object.is_revoke()

    handling_caveats = DBIncidentPatch.handling_to_draft(root_edge_object.obj, "handling_caveat")

    request.breadcrumbs([("Catalog", "")])
    return render(request, "catalog_review.html", {
        "root_id": id,
        "package": data["package"],
        "trust_groups": json.dumps(root_edge_object.tg),
        "validation_info": data["validation_info"],
        "kill_chain_phases": {item['phase_id']: item['name'] for item in KILL_CHAIN_PHASES},
        "back_links": json.dumps(back_links),
        "edges": json.dumps(data["edges"]),
        'view_url': '/' + CLIPPY_TYPES[root_edge_object.doc['type']].replace(' ', '_').lower() + (
            '/view/%s/' % urllib.quote(id)),
        'edit_url': '/' + CLIPPY_TYPES[root_edge_object.doc['type']].replace(' ', '_').lower() + (
            '/edit/%s/' % urllib.quote(id)),
        'visualiser_url': '/adapter/certuk_mod/visualiser/%s' % urllib.quote(id),
        'clone_url': "/adapter/certuk_mod/clone_direct/%s" % urllib.quote(id),
        "revisions": json.dumps(root_edge_object.revisions),
        "revision": revision,
        "sightings": sightings,
        'ajax_uri': reverse('catalog_ajax'),
        "can_revoke": can_revoke,
        "can_purge": can_purge,
        "handling_caveats": json.dumps(handling_caveats)
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


def purge_old_handling_caveats(edge_object):
    markings = edge_object.obj.handling.markings[0].marking_structures
    edge_object.obj.handling.markings[0].marking_structures = [marking for marking in markings if
                                                               marking.marking_model_name != HANDLING_CAVEAT]


def append_handling(edge_object, handling_markings):
    if getattr(edge_object.obj, "handling", None) is None:
        edge_object.obj.handling = make_handling(edge_object.ty)
    else:
        purge_old_handling_caveats(edge_object)

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
def observable_extract(request, output_format, obs_type_filter, id_, revision, extra = "none"):
    revision = "latest"  # override as not sure if it makes sense to use the revision.

    def text_writer(value, obs_type):
        if obs_type == obs_type_filter or obs_type_filter == "all":
            return value + os.linesep
        return ""

    def snort_writer(value, obs_type):
        if obs_type == obs_type_filter or obs_type_filter == "all":
            snort_val = generate_snort(value, obs_type, id_.split(':', 1)[1].split('-', 1)[1])
            if snort_val:
                return snort_val + os.linesep
        return ""

    def not_implemented_writer(*args):
        return ""

    result = ""
    if output_format == "text":
        writer = text_writer
    elif output_format == "SNORT":
        writer = snort_writer
    else:
        writer = not_implemented_writer
        result = "%s not implemented" % output_format

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

        stack.extend([edge.id_ for edge in eo.edges])

        if eo.ty != 'obs':
            continue

        if eo.apidata.has_key("observable_composition"):
            continue

        result += writer(eo.summary['value'], eo.summary['type'])

    if (extra == "download"):
        response = HttpResponse(content_type='text/txt')
        response['Content-Disposition'] = 'attachment; filename="%s_%s_%s.txt"' % (output_format, obs_type_filter, id_)
        response.write(result)
    else :
        response = HttpResponse(json.dumps({"observables-found" : True if result else False}), content_type='text/txt')
    return response
