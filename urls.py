
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^build/$', 'adapters.cert-ind-build.views.indicator_build', name='cert_ind_build')
)

navitems = [
    ('CERT-UK Indicator Builder', 'cert_ind_build')
]

