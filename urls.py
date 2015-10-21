
from url_helper import replace_patterns
from django.conf.urls import patterns, url
from indicator.urls import urlpatterns as original_indicator_urls


# Our own urls
urlpatterns = []

# Add/replace module urls
replace_patterns(
    original_indicator_urls,
    '',
    patterns(
        'adapters.cert-ind-build',
        url(r'^static/(?P<path>[\S]+)$', 'views.static', name='cert_ind_build_static_content'),
        url(r'^build/$', 'views.indicator_build', name='cert_ind_build')
    )
)


navitems = []
