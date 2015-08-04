# Copyright 2013-2015 Soltra
# All Rights Reserved
# See LICENSE.txt for more information.

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^review/$', 'adapters.publisher.views.review', name='publisher_review'),
                       url(r'^missing/$', 'adapters.publisher.views.not_found', name='publisher_not_found'),
                       #    url(r'^publish/$', 'adapters.publisher.views.publish', name='publisher_publish'),
                       )

navitems = [
    ('External Publisher', 'publisher_review'),
]
