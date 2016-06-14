from adapters.certuk_mod.patch import indicator_patch, observable_patch, incident_patch, clone_views
from adapters.certuk_mod.builder import CUSTOM_OBSERVABLES
from adapters.certuk_mod.builder.cert_observable_object_generator import CERTObservableObjectGenerator
from adapters.certuk_mod.builder.view_seed_data import CERTIndicatorBuilderTemplateDataGenerator
from indicator.indicator_builder import IndicatorBuilder
from indicator import views as original_indicator_views


def apply_customizations():
    # NOTE: only UI customisations should be applied here; core behaviour patches belong in certuk_mod/__init__.py
    indicator_patch.apply_patch()
    incident_patch.apply_patch()
    observable_patch.apply_patch(CUSTOM_OBSERVABLES)
    original_indicator_views.observable_object_generator = CERTObservableObjectGenerator()
    original_indicator_views.indicator_builder = IndicatorBuilder(original_indicator_views.observable_object_generator)
    original_indicator_views.view_data_generator = CERTIndicatorBuilderTemplateDataGenerator('Indicator',
                                                                                             'cert-ind-build.html',
                                                                                             original_indicator_views.indicator_builder)

    clone_views.apply_patch()
