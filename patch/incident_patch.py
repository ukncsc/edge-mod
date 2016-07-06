import datetime
import json
from dateutil import parser as dtparser

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.conf import settings

from stix.common import vocabs
from stix.incident import IncidentCategories, IntendedEffects, DiscoveryMethods, ExternalID
from stix.incident.time import Time as StixTime
from stix.extensions.marking.simple_marking import SimpleMarkingStructure

from edge import IDManager, NamespaceNotConfigured, incident
from edge.common import EdgeInformationSource
from edge.generic import WHICH_DBOBJ, FROM_DICT_DISPATCH
from edge.tools import cleanstrings, rgetattr
from incident import views
from rbac import user_can_edit

HANDLING_CAVEAT = 'HANDLING_CAVEAT'
CATEGORIES = vocabs.IncidentCategory._ALLOWED_VALUES
TIME_TYPES = (("first_malicious_action", "First Malicious Action", False),
              ("initial_compromise", "Initial Compromise", False),
              ("first_data_exfiltration", "First Data Exfiltration", False),
              ("incident_discovery", "Incident Discovery", False),
              ("incident_opened", "Incident Opened", True),
              ("containment_achieved", "Containment Achieved", False),
              ("restoration_achieved", "Restoration Achieved", False),
              ("incident_reported", "Incident Reported", False),
              ("incident_closed", "Incident Closed", False))

MARKING_PRIORITIES = ("UK HMG Priority: [C1]", "UK HMG Priority: [C2]", "UK HMG Priority: [C3]")

configuration = settings.ACTIVE_CONFIG

PRETTY_TIME_TYPE = {item[0]: item[1] for item in TIME_TYPES}


def get_build_template(static, id_, id_ns):
    return {
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
        'time_zone': datetime.datetime.now(settings.LOCAL_TZ).tzname()
    }


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

    return render(request, 'cert-inc-build.html', get_build_template(static, id_, id_ns))


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
        'time_zone': datetime.datetime.now(settings.LOCAL_TZ).tzname()
    })


def from_draft_wrapper(wrapped_func):
    wrapped_func = wrapped_func.__func__

    def _w(cls, draft):
        def drop_if_empty(val):
            return val if val else None

        target = wrapped_func(cls, draft)
        target.categories = cleanstrings(draft.get('categories'))

        for key, value in draft.get('time').iteritems():
            DBIncidentPatch.append_config_timezone(value)

        target.time = StixTime()
        StixTime.from_dict(draft.get('time'), target.time)

        target.external_ids = []
        for ex_id in draft.get('external_ids', []):
            target.external_ids.append(ExternalID(ex_id['id'], ex_id['source']))

        target.coordinators = [EdgeInformationSource.from_draft(drop_if_empty(coordinator)) for coordinator in
                               draft.get('coordinators', [])]

        # Edge sets handling by looking for magic strings, tlp and markings, (handing_from draft in handling.py).
        # This is the easiest/least hacky way of adding a new marking.
        handling_caveat = SimpleMarkingStructure(draft.get('handling_caveat'))
        # the following is to mark this as different so on assembling we can recognise
        # between the 2 simple marking structures
        handling_caveat.marking_model_name = HANDLING_CAVEAT

        target.handling.markings[0].marking_structures.append(handling_caveat)

        return target

    return classmethod(_w)


class DBIncidentPatch(incident.DBIncident):
    def __init__(self, obj=None, id_=None, idref=None, timestamp=None, title=None, description=None,
                 short_description=None):
        super(DBIncidentPatch, self).__init__(obj, id_, idref, timestamp, title, description, short_description)

    @classmethod
    def to_draft(cls, inc, tg, load_by_id, id_ns=''):
        draft = super(DBIncidentPatch, cls).to_draft(inc, tg, load_by_id, id_ns)
        if 'responder' in draft:  # fix unbalanced save / load keys in incident.py
            del draft['responder']

        draft['responders'] = [EdgeInformationSource.clone(responder).to_draft() for responder in inc.responders]
        draft['coordinators'] = [EdgeInformationSource.clone(coordinator).to_draft() for coordinator in
                                 inc.coordinators]

        draft['categories'] = [c.value for c in rgetattr(inc, ['categories'], [])]
        if inc.time:
            draft['time'] = inc.time.to_dict();
            for key, value in draft.get('time').iteritems():
                if isinstance(value, basestring):
                    new_value = DBIncidentPatch.convert_to_and_strip_config_timezone(value)
                    draft.get('time')[key] = new_value
                else:
                    value['value'] = DBIncidentPatch.convert_to_and_strip_config_timezone(value['value'])

        if inc.external_ids:
            draft['external_ids'] = []
            for ex_id in inc.external_ids:
                draft['external_ids'].append({'source': ex_id.source, 'id': ex_id.value})


        # Redoing to use correct patched function, can't guarantee correct function if monkey patched
        draft["markings"] = DBIncidentPatch.handling_to_draft(inc, "statement")
        draft["tlp"] = DBIncidentPatch.handling_to_draft(inc, "color")

        draft['handling_caveat'] = DBIncidentPatch.handling_to_draft(inc, "handling_caveat")

        return draft


    @staticmethod
    def handling_to_draft(construct, structure):
        draft = {}
        draft[structure] = []
        handling = rgetattr(construct, ['handling'], '')
        if handling:
            for marking in handling.markings:
                for marking_structure in marking.marking_structures:
                    # stops it adding handling_caveats to marking even though both are in simple marking structures
                    if getattr(marking_structure, 'marking_model_name', None):
                        # retrieve all simple marking statements for handling_caveats
                        if structure == "handling_caveat":
                            draft[structure].append(getattr(marking_structure, 'statement', None))
                    else:
                        if getattr(marking_structure, structure, None):
                            draft[structure].append(getattr(marking_structure, structure, None))
        return draft[structure]


    @staticmethod
    def append_config_timezone(time_dict):
        offset = datetime.datetime.now(settings.LOCAL_TZ).isoformat()[-6:]
        time_dict['value'] = time_dict.get('value') + offset

    @staticmethod
    def convert_to_and_strip_config_timezone(time_str):
        dt_in = dtparser.parse(time_str)
        return dt_in.astimezone(settings.LOCAL_TZ).isoformat()[:-6]

    def update_with(self, update_obj, update_timestamp=True):
        super(DBIncidentPatch, self).update_with(update_obj, update_timestamp)
        self.categories = None
        IncidentCategories.from_dict(update_obj.categories.to_dict(), self.categories)
        if update_obj.time:
            self.time = StixTime.from_dict(update_obj.time.to_dict())
        self.coordinators = update_obj.coordinators

        self.intended_effects = IntendedEffects()
        self.discovery_methods = DiscoveryMethods()

        IntendedEffects.from_dict(update_obj.intended_effects.to_dict(), self.intended_effects)
        DiscoveryMethods.from_dict(update_obj.discovery_methods.to_dict(), self.discovery_methods)

        self.external_ids = []
        for ex_id in update_obj.external_ids:
            self.external_ids.append(ExternalID(ex_id.value, ex_id.source))

    @classmethod
    def api_from_dict(cls, data):
        return cls.from_dict(data)


def apply_patch():
    WHICH_DBOBJ['inc'] = DBIncidentPatch
    FROM_DICT_DISPATCH['inc'] = DBIncidentPatch.api_from_dict
    views.incident_view = incident_view
    views.incident_build = incident_build
    incident.DBIncident.from_draft = from_draft_wrapper(incident.DBIncident.from_draft)
