
from url_helper import replace_patterns
from django.conf.urls import patterns, url
from indicator.urls import urlpatterns as original_indicator_urls
from repository.urls import urlpatterns as core_url_patterns


urlpatterns = []

url_overrides = replace_patterns(
    original_indicator_urls,
    '',
    patterns(
        'adapters.cert-ind-build',
        url(r'^static/(?P<path>[\S]+)$', 'views.static', name='cert_ind_build_static_content'),
        url(r'^build/$', 'views.indicator_build', name='cert_ind_build')
    )
)

core_url_patterns = replace_patterns(
    core_url_patterns,
    '',
    patterns(
        '',
        url(r'^indicator/', url_overrides)
    )
)

navitems = []
