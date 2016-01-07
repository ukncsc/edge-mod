# Copyright 2013-2015 Soltra
# All Rights Reserved
# See LICENSE.txt for more information.

from django.conf.urls import patterns, url
from repository.adaptertools import AdapterInfo
from repository.settings import TEMPLATE_DIRS

# load our templates first
this_adapter = next(adapter for adapter in AdapterInfo.scan() if adapter.name == 'certuk_mod')
if this_adapter:
    for dir_ in this_adapter.find_subdir('templates/'):
        TEMPLATE_DIRS = (dir_,) + TEMPLATE_DIRS

# We have to do this if we want to test our urlconf is correct, because of the way the adapter framework imports
# urls. The mapped views (in Edge) are of the form 'adapters.<adapter_name>.<view_module>.<view_name>', which won't
# resolve in our unit tests (unless we run the tests from within Edge!).

publisher_urls = [
    (r'^static/(?P<path>[\S]+)$', 'views.static', 'static_content'),
    (r'^review/$', 'views.discover', 'publisher_discover'),
    (r'^review/(?P<id_>[A-Za-z][\w\d-]+:[A-Za-z]+-[A-Fa-f\d]{8}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{12})$', 'views.review', 'publisher_review'),
    (r'^missing/$', 'views.not_found', 'publisher_not_found'),
    (r'^config/$', 'views.config', 'publisher_config'),
    (r'^duplicates/$', 'views.duplicates_finder', 'duplicates_finder'),
    (r'^duplicates/(?P<typ>ind|obs|act|ttp|cam|inc|coa|tgt|pkg)$', 'views.ajax_load_duplicates', 'duplicates_duplicates_loader'),
    (r'^duplicates/object/(?P<id_>[A-Za-z][\w\d-]+:[A-Za-z]+-[A-Fa-f\d]{8}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{4}-[A-Fa-f\d]{12})$', 'views.ajax_load_object', 'duplicates_object_loader'),
    (r'^ajax/get_sites/$', 'views.ajax_get_sites', None),
    (r'^ajax/set_publish_site/$', 'views.ajax_set_publish_site', None),
    (r'^ajax/publish/$', 'views.ajax_publish', None),
    (r'^ajax/validate/$', 'views.ajax_validate', None),
    (r'^ajax/get_retention_config/$', 'views.ajax_get_retention_config', None),
    (r'^ajax/set_retention_config/$', 'views.ajax_set_retention_config', None),
    (r'^ajax/import/(?P<username>\S+)$', 'views.ajax_import', None),
]

publisher_url_patterns = [url(item[0], item[1], name=item[2]) for item in publisher_urls]

urlpatterns = patterns('adapters.certuk_mod.views', *publisher_url_patterns)

navitems = [
    ('External Publisher', 'publisher_discover'),
    ('Duplicates Finder', 'duplicates_finder'),
    ('CERT-UK Configuration', 'publisher_config')
]
