import os
import re
import urllib2

from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from users.decorators import superuser_or_staff_role, json_body

from package_publisher import Publisher
from publisher_config import PublisherConfig
from package_generator import PackageGenerator
from publisher_edge_object import PublisherEdgeObject
from validation.package.validator import PackageValidationInfo
from cert_observable_object_generator import CERTObservableObjectGenerator
from indicator.indicator_builder import IndicatorBuilder
from view_seed_data import CERTIndicatorBuilderTemplateDataGenerator
from indicator import views as original_views

objectid_matcher = re.compile(
    # {STIX/ID Alias}:{type}-{GUID}
    r".*/([a-z][\w\d-]+:[a-z]+-[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})/?$",
    re.IGNORECASE  # | re.DEBUG
)
original_views.observable_object_generator = CERTObservableObjectGenerator()
original_views.indicator_builder = IndicatorBuilder(original_views.observable_object_generator)
original_views.view_data_generator = CERTIndicatorBuilderTemplateDataGenerator('Indicator', 'cert-ind-build.html',
                                                                               original_views.indicator_builder)


@login_required
def static(request, path):
    clean_path = urllib2.unquote(path)
    if "../" not in clean_path:
        return FileResponse(
            open(os.path.dirname(__file__) + "/static/" + clean_path, mode="rb")
        )
    else:
        return HttpResponseNotFound()


@login_required
def discover(request):
    referrer = urllib2.unquote(request.META.get("HTTP_REFERER", ""))
    match = objectid_matcher.match(referrer)
    if match is not None and len(match.groups()) == 1:
        id_ = match.group(1)
        return redirect("publisher_review", id_=id_)
    else:
        return redirect("publisher_not_found")


@login_required
def review(request, id_):
    root_edge_object = PublisherEdgeObject.load(id_)
    package = PackageGenerator.build_package(root_edge_object)
    validation_info = PackageValidationInfo.validate(package)
    request.breadcrumbs([("Publisher", "")])
    return render(request, "publisher_review.html", {
        "root_id": id_,
        "package": package,
        "validation_info": validation_info
    })


@login_required
def not_found(request):
    return render(request, "publisher_not_found.html", {})


@login_required
@superuser_or_staff_role
def config(request):
    request.breadcrumbs([("Publisher Configuration", "")])
    return render(request, "publisher_config.html", {})


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


@login_required
@json_body
def ajax_publish(request, data):
    success = True
    error_message = ""

    try:
        root_id = data['root_id']
        edge_object = PublisherEdgeObject.load(root_id)
        package = PackageGenerator.build_package(edge_object)
        namespace_info = edge_object.ns_dict()
        Publisher.push_package(package, namespace_info)
    # Narrow down which exceptions we catch...?
    except Exception, e:
        success = False
        error_message = e.message

    # The whole try/except... return { success.. } thing seems repeated quite a bit for
    # our ajax handlers (and also in the core code)...
    return {
        'success': success,
        'error_message': error_message
    }
