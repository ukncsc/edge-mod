from url_helper import replace_patterns
from django.conf.urls import patterns, url
from indicator.urls import urlpatterns as original_indicator_urls
from repository.adaptertools import AdapterInfo
from repository.settings import TEMPLATE_DIRS

# load our templates first
this_adapter = next(adapter for adapter in AdapterInfo.scan() if adapter.name == 'cert-ind-build')
if this_adapter:
    for dir_ in this_adapter.find_subdir('templates/'):
        TEMPLATE_DIRS = (dir_,) + TEMPLATE_DIRS

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
