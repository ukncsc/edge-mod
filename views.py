import os
import urllib2
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib import messages

from edge import NamespaceNotConfigured

from cert_observable_object_generator import CERTObservableObjectGenerator
from indicator.indicator_builder import IndicatorBuilder
from indicator.view_seed_data import IndicatorBuilderTemplateDataGenerator


observable_object_generator = CERTObservableObjectGenerator()
indicator_builder = IndicatorBuilder(observable_object_generator)
view_data_generator = IndicatorBuilderTemplateDataGenerator('Indicator', 'cert-ind-build.html', indicator_builder)


@login_required
def static(request, path):
    clean_path = urllib2.unquote(path)
    if "../" not in clean_path:
        return FileResponse(
            open(os.path.dirname(__file__) + "/static/" + clean_path, mode="rb")
        )
    else:
        return HttpResponseNotFound()


@login_required
def indicator_build(request):

    request.breadcrumbs([(view_data_generator.title + ' Edit', "/indicator/build")])

    try:
        view_data = view_data_generator.get_new_item_builder_template_data(request)
    except NamespaceNotConfigured as e:
        messages.info(request, e.message)
        return redirect('/setup')
    else:
        return render(request, view_data['template_url'], view_data['template_params'])
