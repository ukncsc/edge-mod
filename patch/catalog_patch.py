import dateutil
from bson import ObjectId
from datetime import timedelta
from mongoengine.connection import get_db
from mongoengine import DoesNotExist

from django.contrib.auth.decorators import login_required
from users.models import Repository_User
from users.decorators import json_body
from users.tools import jstime
from clippy.models import CLIPPY_TYPES
from edge.tools import Optional
from edge.sightings import getSightingsFollowHash
from edge.revoke import StixRevoke
from edge.observable import CYBOX_SHORT_DESCRIPTION
from catalog import views

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

EDGE_DEPTH_LIMIT = 2
MAGIC_QUERY_LIMIT = 20000
ADAPTER_CATALOG_URL = '/adapter/certuk_mod/review/%s'

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
        'view_url': ADAPTER_CATALOG_URL % doc['_id'],
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

@json_body
@login_required
def ajax_load_catalog_patch(request, d):
    req_size = int(d.pop('size', 0))
    req_type = d.pop('type', '').strip()
    req_offset = int(d.pop('offset', 0))
    req_search = d.pop('search', '').strip()
    req_datefilter = d.pop('datefilter', '')
    if d: raise Exception("json request included unknown items")

    def filter_keywords(keywords):
        if keywords:
            search_for_wrapped = ' '.join(word if '"' in word else '"' + word + '"' for word in keywords.split(' '))
            return {'$text': {'$search': search_for_wrapped}}
        else:
            return {}
    def filter_date(datefilter):
        if datefilter:
            try:
                df_lower = dateutil.parser.parse(datefilter)
                df_upper = df_lower + timedelta(days=1)
                return {'created_on': {'$gte': df_lower, '$lt': df_upper}}
            except ValueError:
               pass # don't let a bad date format cause a stack trace
        return {}
    def filter_type(type_):
        return {'type': type_} if type_ in CLIPPY_TYPES else {}
    def filter_out_composite_observables():
        return {'data.summary.type': {'$ne': 'ObservableComposition'}}
    def filter_out_envelopes():
        return {'$or': [{'type': {'$ne': 'pkg'}}, {'type': 'pkg', 'data.summary.title': {'$exists': True}}]}

    def magic_gather_and_sort(criteria, offset, size):

        def only_unique_by_hash(cursor):
            hashes = set()
            counter = 0
            for doc in cursor:
                counter += 1
                if doc['data']['hash'] in hashes: continue
                hashes.add(doc['data']['hash'])
                yield counter, doc

        required = {'_id': 1, 'created_on': 1, 'data.hash': 1}
        cursor = get_db().stix.find(criteria, required, skip=0, limit=MAGIC_QUERY_LIMIT)

        data = []
        scan_count = 0
        unique_count = 0
        for scan_count, doc in only_unique_by_hash(cursor):
            unique_count += 1
            if len(data) < 1000 + offset:
                data.append({'created_on': doc['created_on'], '_id': doc['_id']})
            else:
                data = sorted(data, key=lambda item: item['created_on'], reverse=True)
                del data[offset + size : len(data)]

        data = sorted(data, key=lambda item: item['created_on'], reverse=True)
        del data[0 : offset]
        del data[size : len(data)]
        return data, unique_count, scan_count

    total_count = get_db().stix.find().count()

    if total_count > MAGIC_QUERY_LIMIT and (not req_type) and (not req_search):
        # No criteria and a LOT of data in the database
        no_criteria = True
        count = total_count
        unreliable_sort = True
        results = []
    else:
        no_criteria = False
        query = {'txn': None}
        query.update(filter_date(req_datefilter))
        query.update(filter_type(req_type))
        query.update(filter_keywords(req_search))
        query.update(filter_out_composite_observables())
        query.update(filter_out_envelopes())
        query.update(request.user.filters())

        data, unique_count, scan_count = magic_gather_and_sort(query, req_offset, req_size)
        count = unique_count
        unreliable_sort = scan_count >= MAGIC_QUERY_LIMIT
        results = (doc['_id'] for doc in data)

    loaded = (load_object_for_catalog(idref) for idref in results)
    return {
        'data': [object_to_js_for_catalog(doc) for doc in loaded],
        'no_criteria': no_criteria,
        'unreliable_sort': unreliable_sort,
        'count': count,
        'success': True,
    }

def apply_patch():
    views.ajax_load_catalog = ajax_load_catalog_patch
