from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from django.conf import settings

from edge import IDManager, NamespaceNotConfigured
from incident import views
from rbac import user_can_edit

import json

@login_required
def incident_build(request):
    request.breadcrumbs([("Incident Edit", "/incident/build/")])

    static = views.get_static(request.user)
    configuration = settings.REPOCONFIG()
    id_ns = None
    id = None
    try:
        id_ns = IDManager().get_namespace()
        id = IDManager().get_new_id('incident')
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')

    return render(request, 'cert-inc-build.html', {
        'mode': 'Build',
        'id': id,
        'id_ns': id_ns,
        'default_tlp' : configuration.by_key('default_tlp'),
        'effects': json.dumps(static['effects']),
        'statuses': json.dumps(static['statuses']),
        'confidences': json.dumps(static['confidences']),
        'tlps': json.dumps(static['tlps']),
        'trustgroups': json.dumps(static['trustgroups']),
        'discovery_methods': json.dumps(static['discovery_methods']),
        'intended_effects': json.dumps(static['intended_effects']),
        'ajax_uri': reverse('incident_ajax'),
        'object_type': "incident",
    })


@login_required
def incident_view(request, id, edit=False):

    if edit:
        request.breadcrumbs([ ("Incident Edit","/incident/edit/") ])
        mode = "Edit"
    else:
        request.breadcrumbs([ ("Incident View","/incident/build/") ])
        mode = "View"

    static = views.get_static(request.user)
    return render(request, 'cert-inc-build.html', {
        'mode': mode,
        'object_type'      : 'incident',
        'id': id,
        'object_type': "incident",
        'edit_allowed' : user_can_edit(request.user, id),
        'effects': json.dumps(static['effects']),
        'statuses': json.dumps(static['statuses']),
        'confidences': json.dumps(static['confidences']),
        'tlps': json.dumps(static['tlps']),
        'trustgroups': json.dumps(static['trustgroups']),
        'discovery_methods': json.dumps(static['discovery_methods']),
        'intended_effects': json.dumps(static['intended_effects']),
        'ajax_uri': reverse('incident_ajax'),
        'object_type': "incident",
    })


def apply_patch():
    views.incident_view = incident_view
    views.incident_build = incident_build
