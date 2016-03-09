import json
import json
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from django.core.urlresolvers import reverse

from edge import IDManager, NamespaceNotConfigured
from indicator import views as ind_views
from incident import views as inc_views
from campaign import views as cam_views
from course import views as coa_views
from threat_actor import views as act_views
from exploit_target import views as tgt_views
from ttp import views as ttp_views

from ttp.urls import urlpatterns as ttp_urls
from indicator.urls import urlpatterns as ind_urls
from incident.urls import urlpatterns as inc_urls
from campaign.urls import urlpatterns as cam_urls
from course.urls import urlpatterns as coa_urls
from exploit_target.urls import urlpatterns as tgt_urls
from threat_actor.urls import urlpatterns as act_urls

from rbac import user_can_edit


from adapters.certuk_mod.patch.incident_patch import get_build_template as inc_template

ttp_urls.append(url(r'^build/(?P<id>.+)/$', 'ttp.views.ttp_build_from_clone'))
ind_urls.append(url(r'^build/(?P<id>.+)/$', 'indicator.views.ind_build_from_clone'))
inc_urls.append(url(r'^build/(?P<id>.+)/$', 'incident.views.inc_build_from_clone'))
cam_urls.append(url(r'^build/(?P<id>.+)/$', 'campaign.views.cam_build_from_clone'))
coa_urls.append(url(r'^build/(?P<id>.+)/$', 'course.views.coa_build_from_clone'))
tgt_urls.append(url(r'^build/(?P<id>.+)/$', 'exploit_target.views.tgt_build_from_clone'))
act_urls.append(url(r'^build/(?P<id>.+)/$', 'threat_actor.views.act_build_from_clone'))

configuration = settings.ACTIVE_CONFIG


@login_required
def ind_build_from_clone(request, id):
    request.breadcrumbs([(ind_views.view_data_generator.title + ' Edit', "/indicator/build")])

    try:
        view_data = ind_views.view_data_generator.get_new_item_builder_template_data(request)
        view_data['template_params']['draft_id'] = id
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')
    else:
        return render(request, view_data['template_url'], view_data['template_params'])


@login_required
def inc_build_from_clone(request, id):
    request.breadcrumbs([("Incident Edit", "/incident/build/")])
    static = inc_views.get_static(request.user)

    try:
        id_ns = IDManager().get_namespace()
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')

    template = inc_template(static, None, id_ns);
    template['draft_id'] = id

    return render(request, 'cert-inc-build.html', template)


@login_required
def cam_build_from_clone(request, id):
    request.breadcrumbs([("Campaign Edit", "/campaign/build/")])

    static = cam_views.get_static(request.user)

    try:
        id_ns = IDManager().get_namespace()
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')

    return render(request, 'cert-cam-build.html', {
        'mode': 'Build',
        'default_tlp': configuration.by_key('default_tlp'),
        'id': None,
        'id_ns': id_ns,
        'intended_effects': json.dumps(static['intended_effects']),
        'statuses': json.dumps(static['statuses']),
        'confidences': json.dumps(static['confidences']),
        'tlps': json.dumps(static['tlps']),
        'trustgroups': json.dumps(static['trustgroups']),
        'ajax_uri': reverse('campaign_ajax'),
        'draft_id': id
    })


@login_required
def coa_build_from_clone(request, id):
    request.breadcrumbs([("Course of Action Edit", "/course/build/")])

    static = coa_views.get_static(request.user)

    try:
        id_ns = IDManager().get_namespace()
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')

    return render(request, 'cert-coa-build.html', {
        'id': None,
        'mode': 'Build',
        'id_ns': id_ns,
        'ajax_uri': reverse('course_ajax'),
        'default_tlp': configuration.by_key('default_tlp'),
        'tlps': json.dumps(static['tlps']),
        'stages': json.dumps(static['stages']),
        'impacts': json.dumps(static['confidence_list']),
        'coa_types': json.dumps(static['coa_types']),
        'confidences': json.dumps(static['confidence_list']),
        'trustgroups': json.dumps(static['trustgroups']),
        'object_type': "course_of_action",
        'draft_id': id
    })


@login_required
def act_build_from_clone(request, id):
    request.breadcrumbs([("Threat Actor Edit", "/threat_actor/build/")])
    static = act_views.get_static(request.user)

    try:
        id_ns = IDManager().get_namespace()
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')

    return render(request, 'cert-act-build.html', {
        'id': None,
        'id_ns': id_ns,
        'mode': 'Build',
        'object_type': 'threat_actor',
        'edit_allowed': user_can_edit(request.user, id),
        'ajax_uri': reverse('threat_actor_ajax'),
        'default_tlp': configuration.by_key('default_tlp'),
        'tlps': json.dumps(static['tlps']),
        'planning': json.dumps(static['planning']),
        'confidences': json.dumps(static['confidences']),
        'motivations': json.dumps(static['motivations']),
        'trustgroups': json.dumps(static['trustgroups']),
        'act_type_list': json.dumps(static['act_type_list']),
        'sophistication': json.dumps(static['sophistication']),
        'intended_effects': json.dumps(static['intended_effects']),
        'draft_id': id
    })


@login_required
def tgt_build_from_clone(request, id):
    request.breadcrumbs([("Exploit Target Edit", "/exploit_target/build/")])

    static = tgt_views.get_static(request.user)

    try:
        id_ns = IDManager().get_namespace()
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')

    return render(request, 'cert-tgt-build.html', {
        'mode': 'Build',
        'default_tlp': configuration.by_key('default_tlp'),
        'object_type': "exploit_target",
        'id': None,
        'id_ns': id_ns,
        'tlps': json.dumps(static['tlps']),
        'trustgroups': json.dumps(static['trustgroups']),
        'ajax_uri': reverse('exploit_target_ajax'),
        'draft_id': id
    })


@login_required
def ttp_build_from_clone(request, id):
    request.breadcrumbs([("TTP Edit", "/ttp/build/")])

    static = ttp_views.get_static(request.user)

    return render(request, 'cert-ttp-build.html', {
        'id': None,
        'mode': 'Build',
        'object_type': 'ttp',
        'edit_allowed': ttp_views.user_can_edit(request.user, id),
        'ajax_uri': ttp_views.reverse('ttp_ajax'),
        'tlps': json.dumps(static['tlps']),
        'malware': json.dumps(static['malware']),
        'trustgroups': json.dumps(static['trustgroups']),
        'intended_effects': json.dumps(static['intended_effects']),
        'object_type': "ttp",
        'draft_id': id
    })


def apply_patch():
    ttp_views.ttp_build_from_clone = ttp_build_from_clone
    ind_views.ind_build_from_clone = ind_build_from_clone
    inc_views.inc_build_from_clone = inc_build_from_clone
    cam_views.cam_build_from_clone = cam_build_from_clone
    coa_views.coa_build_from_clone = coa_build_from_clone
    act_views.act_build_from_clone = act_build_from_clone
    tgt_views.tgt_build_from_clone = tgt_build_from_clone
