
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from edge import NamespaceNotConfigured

from indicator.observable_object_generator import ObservableObjectGenerator
from indicator.indicator_builder import IndicatorBuilder
from indicator.view_seed_data import IndicatorBuilderTemplateDataGenerator


observable_object_generator = ObservableObjectGenerator()
indicator_builder = IndicatorBuilder(observable_object_generator)
view_data_generator = IndicatorBuilderTemplateDataGenerator('Indicator', 'cert-ind-build.html', indicator_builder)


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
