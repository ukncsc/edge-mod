# Copyright 2013-2015 Soltra
# All Rights Reserved
# See LICENSE.txt for more information.

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^select/$', 'adapters.publisher.views.select', name='publisher_select'),
                       #    url(r'^review/$', 'adapters.publisher.views.review', name='publisher_review'),
                       url(r'^ajax/publish/$', 'adapters.publisher.views.ajax_publish', name='publisher_publish'),
                       )

navitems = [
    ('Publisher', 'publisher_select'),
]
