# Copyright 2013-2015 Soltra
# All Rights Reserved
# See LICENSE.txt for more information.

from django.conf.urls import patterns, url

# We have to do this if we want to test our urlconf is correct, because of the way the adapter framework imports
# urls. The mapped views (in Edge) are of the form 'adapters.<adapter_name>.<view_module>.<view_name>', which won't
# resolve in our unit tests (unless we run the tests from within Edge!).

publisher_urls = [
    (r'^review/$', 'views.review', 'publisher_review'),
    (r'^missing/$', 'views.not_found', 'publisher_not_found'),
    (r'^config/$', 'views.config', 'publisher_config'),
    (r'^ajax/get_sites/$', 'views.ajax_get_sites', None),
    (r'^ajax/set_publish_site/$', 'views.ajax_set_publish_site', None),
    (r'^ajax/publish/$', 'views.ajax_publish', None)
]

publisher_url_patterns = [url(item[0], item[1], name=item[2]) for item in publisher_urls]

urlpatterns = patterns('adapters.publisher', *publisher_url_patterns)

navitems = [
    ('External Publisher', 'publisher_review'),
    ('External Publisher Configuration', 'publisher_config')
]
