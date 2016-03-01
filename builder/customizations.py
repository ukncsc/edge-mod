from adapters.certuk_mod.patch import indicator_patch, inbox_patch, observable_patch, hash_patch, remap_patch
from adapters.certuk_mod.builder import CUSTOM_OBSERVABLES
from adapters.certuk_mod.builder.cert_observable_object_generator import CERTObservableObjectGenerator
from adapters.certuk_mod.builder.view_seed_data import CERTIndicatorBuilderTemplateDataGenerator
from indicator.indicator_builder import IndicatorBuilder
from indicator import views as original_views


def apply_customizations():
    indicator_patch.apply_patch()
    inbox_patch.apply_patch()
    observable_patch.apply_patch(CUSTOM_OBSERVABLES)
    hash_patch.apply_patch()
    original_views.observable_object_generator = CERTObservableObjectGenerator()
    original_views.indicator_builder = IndicatorBuilder(original_views.observable_object_generator)
    original_views.view_data_generator = CERTIndicatorBuilderTemplateDataGenerator('Indicator', 'cert-ind-build.html',
                                                                                   original_views.indicator_builder)
