from django.conf.urls import url
from repository.adaptertools import AdapterInfo
from repository.settings import TEMPLATE_DIRS

# load our templates first
this_adapter = next(adapter for adapter in AdapterInfo.scan() if adapter.name == 'cert-ind-build')
if this_adapter:
    for dir_ in this_adapter.find_subdir('templates/'):
        TEMPLATE_DIRS = (dir_,) + TEMPLATE_DIRS

# Our own urls
urlpatterns = [
    url(r'^static/(?P<path>[\S]+)$', 'adapters.cert-ind-build.views.static', name='cert_ind_build_static_content')
]


navitems = []
