import os
import urllib2
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseNotFound

from cert_observable_object_generator import CERTObservableObjectGenerator
from indicator.indicator_builder import IndicatorBuilder
from indicator.view_seed_data import IndicatorBuilderTemplateDataGenerator
from indicator import views as original_views

original_views.observable_object_generator = CERTObservableObjectGenerator()
original_views.indicator_builder = IndicatorBuilder(original_views.observable_object_generator)
original_views.view_data_generator = IndicatorBuilderTemplateDataGenerator('Indicator', 'cert-ind-build.html', original_views.indicator_builder)


@login_required
def static(request, path):
    clean_path = urllib2.unquote(path)
    if "../" not in clean_path:
        return FileResponse(
            open(os.path.dirname(__file__) + "/static/" + clean_path, mode="rb")
        )
    else:
        return HttpResponseNotFound()
