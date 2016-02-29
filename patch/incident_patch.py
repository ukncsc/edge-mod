import json
import pytz
import datetime
from dateutil import tz

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.conf import settings

from stix.common import vocabs
from stix.incident.time import Time as StixTime
from stix.incident import IncidentCategories

from edge.common import EdgeInformationSource
from edge.generic import WHICH_DBOBJ, FROM_DICT_DISPATCH
from edge.tools import cleanstrings, rgetattr
from edge import IDManager, NamespaceNotConfigured, incident

from incident import views
from rbac import user_can_edit

TIME_ZONE_DESCRIPTIONS = pytz.all_timezones
CATEGORIES = vocabs.IncidentCategory._ALLOWED_VALUES
TIME_TYPES = (("first_malicious_action", "First Malicious Action"),
              ("initial_compromise", "Initial Compromise"),
              ("first_data_exfiltration", "First Data Exfiltration"),
              ("incident_discovery", "Incident Discovery"),
              ("incident_opened", "Incident Opened"),
              ("containment_achieved", "Containment Achieved"),
              ("restoration_achieved", "Restoration Achieved"),
              ("incident_reported", "Incident Reported"),
              ("incident_closed", "Incident Closed"))

MARKING_PRIORITIES = ("UK HMG Priority: [C1]", "UK HMG Priority: [C2]", "UK HMG Priority: [C3]")

configuration = settings.ACTIVE_CONFIG


@login_required
def incident_build(request):
    request.breadcrumbs([("Incident Edit", "/incident/build/")])
    static = views.get_static(request.user)

    try:
        id_ns = IDManager().get_namespace()
        id_ = IDManager().get_new_id('incident')
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')

    return render(request, 'cert-inc-build.html', {
        'mode': 'Build',
        'id': id_,
        'id_ns': id_ns,
        'default_tlp': configuration.by_key('default_tlp'),
        'effects': json.dumps(static['effects']),
        'statuses': json.dumps(static['statuses']),
        'categories': json.dumps(CATEGORIES),
        'time_types_list': json.dumps(TIME_TYPES),
        'marking_priorities': json.dumps(MARKING_PRIORITIES),
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
        request.breadcrumbs([("Incident Edit", "/incident/edit/")])
        mode = "Edit"
    else:
        request.breadcrumbs([("Incident View", "/incident/build/")])
        mode = "View"

    static = views.get_static(request.user)
    return render(request, 'cert-inc-build.html', {
        'mode': mode,
        'object_type': 'incident',
        'id': id,
        'object_type': "incident",
        'edit_allowed': user_can_edit(request.user, id),
        'effects': json.dumps(static['effects']),
        'statuses': json.dumps(static['statuses']),
        'categories': json.dumps(CATEGORIES),
        'time_types_list': json.dumps(TIME_TYPES),
        'marking_priorities': json.dumps(MARKING_PRIORITIES),
        'confidences': json.dumps(static['confidences']),
        'tlps': json.dumps(static['tlps']),
        'trustgroups': json.dumps(static['trustgroups']),
        'discovery_methods': json.dumps(static['discovery_methods']),
        'intended_effects': json.dumps(static['intended_effects']),
        'ajax_uri': reverse('incident_ajax'),
        'object_type': "incident",
    })


def from_draft_wrapper(wrapped_func):
    wrapped_func = wrapped_func.__func__
    def _w(cls, draft):
        target = wrapped_func(cls, draft)
        target.categories = cleanstrings(draft.get('categories'))

        for time_type, _ in TIME_TYPES:
            DBIncidentPatch.append_timezone(draft.get('time').get(time_type))

        target.time = StixTime()
        StixTime.from_dict(draft.get('time'), target.time)
        return target
    return classmethod(_w)

class DBIncidentPatch(incident.DBIncident):
    def __init__(self, obj=None, id_=None, idref=None, timestamp=None, title=None, description=None,
                 short_description=None):
        super(DBIncidentPatch, self).__init__(obj, id_, idref, timestamp, title, description, short_description)

    @classmethod
    def to_draft(cls, inc, tg, load_by_id, id_ns=''):
        draft = super(DBIncidentPatch, cls).to_draft(inc, tg, load_by_id, id_ns)
        if 'responder' in draft: #fix unbalanced save / load keys in incident.py
            del draft['responder']

        draft['responders'] = [EdgeInformationSource.clone(responder).to_draft() for responder in inc.responders ]

        draft['categories'] = [c.value for c in rgetattr(inc, ['categories'], [])]
        if inc.time:
            draft['time'] = inc.time.to_dict();
        return draft

    @staticmethod
    def append_timezone(time_dict):
        # No value
        if time_dict is None or not time_dict.has_key('value'):
            return

        # Already has a timezone offset
        if time_dict.get('value')[-6] is '-' or time_dict.get('value')[-6] is '+':
            return

        offset = datetime.datetime.now(tz.gettz(configuration.by_key('display_timezone'))).strftime('%z')
        time_dict['value'] = time_dict.get('value') + offset[0:3] + ":" + offset[3:5]

    def update_with(self, update_obj, update_timestamp=True):
        super(DBIncidentPatch, self).update_with(update_obj, update_timestamp)
        IncidentCategories.from_dict(update_obj.categories.to_dict(), self.categories)
        if update_obj.time:
            self.time = StixTime.from_dict(update_obj.time.to_dict())


def apply_patch():
    WHICH_DBOBJ['inc'] = DBIncidentPatch
    views.incident_view = incident_view
    views.incident_build = incident_build
    incident.DBIncident.from_draft = from_draft_wrapper(incident.DBIncident.from_draft)
