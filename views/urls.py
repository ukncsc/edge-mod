# Copyright 2013-2015 Soltra
# All Rights Reserved
# See LICENSE.txt for more information.

from django.conf.urls import patterns, url
from repository.adaptertools import AdapterInfo
from repository.settings import TEMPLATE_DIRS
from clippy.models import CLIPPY_TYPES

# load our templates first
this_adapter = next(adapter for adapter in AdapterInfo.scan() if adapter.name == 'certuk_mod')
if this_adapter:
    for dir_ in this_adapter.find_subdir('templates/'):
        TEMPLATE_DIRS = (dir_,) + TEMPLATE_DIRS

VALID_STIX_ID = '[A-Za-z][\w\d-]+:[A-Za-z]+-[A-Fa-f\d]{8}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{12}'
VALID_TYPES = '|'.join(CLIPPY_TYPES.iterkeys())

# We have to do this if we want to test our urlconf is correct, because of the way the adapter framework imports
# urls. The mapped views (in Edge) are of the form 'adapters.<adapter_name>.<view_module>.<view_name>', which won't
# resolve in our unit tests (unless we run the tests from within Edge!).

publisher_urls = [
    (r'^static/(?P<path>[\S]+)$', 'views.static', 'static_content'),
    (r'^review/$', 'views.discover', 'publisher_discover'),
    (r'^review/duplicates/(?P<id_>' + VALID_STIX_ID + ')$', 'views.get_duplicates', 'get_duplicates'),
    (r'^review/handling/', 'views.review_set_handling', 'review_set_handling'),

    (r'^extract/$', 'views.extract', 'extract_stix'),
    (r'^uploaded_stix_extracts/$', 'views.uploaded_stix_extracts', 'uploaded_stix_extracts'),
    (r'^ajax/extract_status/$', 'views.extract_status', 'extract_status'),
    (r'^extract_upload/$', 'views.extract_upload', 'extract_upload'),
    (r'^ajax/extract_list/$', 'views.extract_list', 'extract_list'),
    (r'^ajax/delete_extract/$', 'views.delete_extract', 'delete_extract'),
    (r'^extract_visualiser/(?P<ids>.*)$', 'views.extract_visualiser', 'extract_visualiser'),
    (r'^ajax/extract_visualiser/(?P<id_>' + VALID_STIX_ID + ')$', 'views.extract_visualiser_get', 'extract_visualiser_ajax_view'),
    (r'^ajax/extract_visualiser/item/(?P<node_id>.*)$', 'views.extract_visualiser_item_get', 'extract_visualiser_ajax_item'),
    (r'^ajax/extract_visualiser/merge_observables/.*$', 'views.extract_visualiser_merge_observables', 'extract_visualiser_ajax_merge_observables'),
    (r'^ajax/extract_visualiser/delete_observables/.*$', 'views.extract_visualiser_delete_observables', 'extract_visualiser_ajax_delete_observables'),
    (r'^ajax/extract_visualiser/get_extended/$', 'views.extract_visualiser_get_extended', 'extract_visualiser_get_extended'),

    (r'^incident_timeline/$', 'views.timeline_discover', 'timeline_discover'),
    (r'^incident_timeline/(?P<id_>' + VALID_STIX_ID + ')$', 'views.incident_timeline', 'incident_timeline'),
    (r'^incident_timeline/missing/$', 'views.incident_timeline_not_found', 'incident_timeline_not_found'),
    (r'^ajax/incident_timeline/(?P<id_>' + VALID_STIX_ID + ')$', 'views.ajax_incident_timeline', 'ajax_incident_timeline'),

    (r'^clone/$', 'views.clone', 'clone_to_draft'),
    (r'^review/(?P<id_>' + VALID_STIX_ID + ')$', 'views.review', 'catalog_review'),
    (r'^missing/$', 'views.not_found', 'publisher_not_found'),
    (r'^noclone/(?P<msg>)', 'views.error_with_message', 'error_with_message'),
    (r'^config/$', 'views.config', 'publisher_config'),
    (r'^activity/$', 'views.activity_log', 'activity_log'),
    (r'^ajax/activity_log/(?P<search>.*)$', 'views.ajax_activity_log', None),
    (r'^duplicates/$', 'views.duplicates_finder', 'duplicates_finder'),
    (r'^duplicates/(?P<typ>' + VALID_TYPES + ')$', 'views.ajax_load_duplicates', 'duplicates_duplicates_loader'),
    (r'^duplicates/object/(?P<id_>' + VALID_STIX_ID + ')$', 'views.ajax_load_object', 'duplicates_object_loader'),
    (r'^duplicates/parents/(?P<id_>' + VALID_STIX_ID + ')$', 'views.ajax_load_parent_ids', 'duplicates_parents_loader'),
    (r'^ajax/get_sites/$', 'views.ajax_get_sites', None),
    (r'^ajax/set_publish_site/$', 'views.ajax_set_publish_site', None),
    (r'^ajax/publish/$', 'views.ajax_publish', None),
    (r'^ajax/validate/$', 'views.ajax_validate', None),
    (r'^import/(?P<username>\S+)$', 'views.ajax_import', None),

    (r'^ajax/get_retention_config/$', 'views.ajax_get_retention_config', None),
    (r'^ajax/set_retention_config/$', 'views.ajax_set_retention_config', None),
    (r'^ajax/reset_retention_config/$', 'views.ajax_reset_retention_config', None),
    (r'^ajax/get_purge_task_status/$', 'views.ajax_get_purge_task_status', None),
    (r'^ajax/run_purge_task/$', 'views.ajax_run_purge', None),

    (r'^ajax/get_fts_config/$', 'views.ajax_get_fts_config', None),
    (r'^ajax/set_fts_config/$', 'views.ajax_set_fts_config', None),
    (r'^ajax/reset_fts_config/$', 'views.ajax_reset_fts_config', None),
    (r'^ajax/get_fts_task_status/$', 'views.ajax_get_fts_task_status', None),
    (r'^ajax/run_fts_task/$', 'views.ajax_run_fts', None),

    (r'^ajax/get_datetime/$', 'views.ajax_get_datetime', None),
    (r'^config/get_cert_config/$', 'views.ajax_get_cert_config', None),
    (r'^config/get_crm_config/$', 'views.ajax_get_crm_config', None),
    (r'^config/set_crm_config/$', 'views.ajax_set_crm_config', None),
    (r'^config/get_sharing_groups/$', 'views.ajax_get_sharing_groups', None),
    (r'^config/set_sharing_groups/$', 'views.ajax_set_sharing_groups', None),

    (r'^visualiser/$', 'views.visualiser_discover', 'visualiser_discover'),
    (r'^visualiser/missing/$', 'views.visualiser_not_found', 'visualiser_not_found'),
    (r'^visualiser/(?P<id_>' + VALID_STIX_ID + ')$', 'views.visualiser_view', 'visualiser_view'),
    (r'^ajax/visualiser/(?P<id_>' + VALID_STIX_ID + ')$', 'views.visualiser_get', 'visualiser_ajax_view'),
    (r'^ajax/visualiser/item/(?P<id_>' + VALID_STIX_ID + ')$', 'views.visualiser_item_get', 'visualiser_ajax_item'),
    (r'^ajax/visualiser/get_extended/.*$', 'views.visualiser_get_extended', 'visualiser_ajax_get_extended')
]

publisher_url_patterns = [url(item[0], item[1], name=item[2]) for item in publisher_urls]

urlpatterns = patterns('adapters.certuk_mod.views', *publisher_url_patterns)

navitems = [
    ('External Publisher', 'publisher_discover'),
    ('Extract Stix', 'extract_stix'),
    ('Uploaded Stix Extracts', 'uploaded_stix_extracts'),
    ('Clone to Draft', 'clone_to_draft'),
    ('Visualiser', 'visualiser_discover'),
    ('Incident Timeline', 'timeline_discover'),
    # ('Duplicates Finder', 'duplicates_finder'),
    ('Activity Log', 'activity_log'),
    ('CERT-UK Configuration', 'publisher_config')
]
