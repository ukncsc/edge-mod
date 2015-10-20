
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'adapters.cert-ind-build',
    url(r'^static/(?P<path>[\S]+)$', 'views.static', name='cert_ind_build_static_content'),
    url(r'^build/$', 'views.indicator_build', name='cert_ind_build')
)

navitems = [
    ('CERT-UK Indicator Builder', 'cert_ind_build')
]

