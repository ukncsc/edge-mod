
from indicator.view_seed_data import IndicatorBuilderTemplateDataGenerator
from kill_chain_definition import KILL_CHAIN_PHASES


class CERTIndicatorBuilderTemplateDataGenerator(IndicatorBuilderTemplateDataGenerator):

    def __init__(self, title, builder_url, indicator_builder):
        super(CERTIndicatorBuilderTemplateDataGenerator, self).__init__(title, builder_url, indicator_builder)

    def _get_builder_template_params(self, request, id, url, extra_params=None):
        template_params = super(CERTIndicatorBuilderTemplateDataGenerator, self)._get_builder_template_params(
            request, id, url, extra_params
        )
        template_params['template_params']['kill_chain_phase_list'] = KILL_CHAIN_PHASES
        return template_params
