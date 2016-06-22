from bson import ObjectId
from mongoengine.connection import get_db
from mongoengine import DoesNotExist

from users.models import Repository_User
from users.tools import jstime
from clippy.models import CLIPPY_TYPES
from edge.tools import Optional
from edge.sightings import getSightingsFollowHash
from edge.revoke import StixRevoke
from edge.observable import CYBOX_SHORT_DESCRIPTION

SUMMARY_FIELDS = {
    'inc': ('title', 'status', 'confidence', 'effects'),
    'cam': ('title', 'status', 'confidence', 'names'),
    'ind': ('title', 'type', 'producer'),
    'obs': ('title', 'category', 'type', 'sightings', 'value'),
    'ttp': ('title', 'description'),
    'act': ('title', 'confidence'),
    'coa': ('title', 'type'),
    'pkg': ('title', 'source', 'intent'),
    'tgt': ('title', 'short_description'),
}

SUMMARY_DEFAULTS = {
    'title': '(untitled)',
}

OBJECT_TO_JS_REQUIRED = {
    '_id': 1, 'created_on': 1, 'created_by': 1, 'type': 1,
    'data.summary': 1, 'data.hash': 1, 'data.etlp': 1, 'data.idns': 1
}


def load_object_for_catalog(idref):
    doc = get_db().stix.find_one({'_id': idref}, OBJECT_TO_JS_REQUIRED)
    if doc: return doc
    raise DoesNotExist()


def object_to_js_for_catalog(doc):

    assert isinstance(doc['created_by'], ObjectId)
    assert doc['type'] in SUMMARY_FIELDS

    def display_tlp(summary_tlp, effective_tlp):
        if summary_tlp:
            tlp = summary_tlp
        elif effective_tlp:
            tlp = effective_tlp
        else:
            tlp = ''

        return tlp if tlp != 'NULL' else ''

    try:
        user = Repository_User.objects.get(id=doc['created_by'])
    except DoesNotExist:
        user_fullname = "--Unknown--"
        user_organization = ''
    else:
        user_fullname = "%s %s" % (user.first_name, user.last_name)
        user_organization = Optional(user).organization.value()

    def maybeTrim(value, width=80):
        if len(value.strip()) > width:
            return value.strip()[:width-3] + "..."
        return value

    summary = doc['data']['summary']

    revoked_by = StixRevoke.sources(doc['_id'])
    revoked = True if revoked_by else False

    data = {
        'id': doc['_id'],
        'idns': doc['data'].get('idns'),
        'tlp': display_tlp(summary.get('tlp'), doc['data'].get('etlp')),
        'markings': summary.get("markings", []),
        'date': jstime(doc['created_on']),
        'user': user_fullname,
        'revoked': revoked,
        'view_url': '/adapter/certuk_mod/review/%s' % doc['_id'],
        'obj_type': doc['type'],
        'obj_type_long': CLIPPY_TYPES[doc['type']],
        'download_url': '/catalog/download/%s/%s' % (doc['type'], doc['_id']),
        'organization': user_organization,
    }

    for field in SUMMARY_FIELDS[doc['type']]:
        if hasattr(summary.get(field, None), '__iter__'):
            data[field] = maybeTrim(', '.join(summary.get(field, SUMMARY_DEFAULTS.get(field, ''))))
        else:
            data[field] = maybeTrim(summary.get(field, SUMMARY_DEFAULTS.get(field, '')))

    if doc['type'] == 'obs':
        data['sightings'] = getSightingsFollowHash(doc['data']['hash'])
        data['observable_type'] = CYBOX_SHORT_DESCRIPTION.get(data['type'], '')

    return data

def apply_patch():
    EdgeObject.capsulize = capsulize_patch
