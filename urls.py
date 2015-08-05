# Copyright 2013-2015 Soltra
# All Rights Reserved
# See LICENSE.txt for more information.

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^review/$', 'adapters.publisher.views.review', name='publisher_review'),
                       url(r'^missing/$', 'adapters.publisher.views.not_found', name='publisher_not_found'),
                       url(r'^config/$', 'adapters.publisher.views.config', name='publisher_config'),
                       url(r'^ajax/get_sites/$', 'adapters.publisher.views.ajax_get_sites'),
                       url(r'^ajax/set_publish_site/$', 'adapters.publisher.views.ajax_set_publish_site')
                       #    url(r'^publish/$', 'adapters.publisher.views.publish', name='publisher_publish'),
                       )

navitems = [
    ('External Publisher', 'publisher_review'),
    ('External Publisher Configuration', 'publisher_config')
]
