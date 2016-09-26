from stix.extensions.test_mechanism.snort_test_mechanism import SnortTestMechanism
from stix.extensions.test_mechanism.yara_test_mechanism import YaraTestMechanism
from edge.generic import WHICH_DBOBJ
from indicator.indicator_builder import IndicatorBuilder
from edge.tools import rgetattr
from edge import relate
from edge.generic import ApiObject, EdgeObject
from edge.indicator import DBIndicator
from edge.inbox import InboxProcessorForBuilders, InboxItem
from adapters.certuk_mod.builder.cert_observable_object_generator import CERTObservableObjectGenerator

from edge.handling import lines2list, handling_from_draft
from cybox.core import ObservableComposition, Object, Observable
from datetime import datetime
import logging
from edge.common import EdgeInformationSource, EdgeIdentity


class DBIndicatorPatch(DBIndicator):
    def __init__(self, obj=None, id_=None, idref=None, timestamp=None, title=None, description=None,
                 short_description=None):
        super(DBIndicatorPatch, self).__init__(obj, id_, idref, timestamp, title, description, short_description)

    @classmethod
    def to_draft(cls, indicator, tg, load_by_id, id_ns=''):
        draft = super(DBIndicatorPatch, cls).to_draft(indicator, tg, load_by_id, id_ns)
        kill_chain_phases = rgetattr(indicator, ['kill_chain_phases'])
        if kill_chain_phases:
            draft['kill_chain_phase'] = rgetattr(kill_chain_phases[0], ['phase_id'], '')

        test_mechanisms = rgetattr(indicator, ['test_mechanisms'])
        if test_mechanisms:
            for test_mechanism in test_mechanisms:
                if isinstance(test_mechanism, SnortTestMechanism):
                    snort_dict = SnortTestMechanism.to_dict(test_mechanism)
                    snort_dict['type'] = 'Snort'
                    draft.setdefault('test_mechanisms', []).append(snort_dict)
                if isinstance(test_mechanism, YaraTestMechanism):
                    yara_dict = YaraTestMechanism.to_dict(test_mechanism)
                    yara_dict['type'] = 'Yara'
                    draft.setdefault('test_mechanisms', []).append(yara_dict)
        return draft


    def map(self):
        pass

    def update_with(self, update_obj, update_timestamp=True):
        super(DBIndicatorPatch, self).update(self, update_obj, update_timestamp)
        self.detection_rules = update_obj.detection_rules


class IndicatorBuilderPatch(IndicatorBuilder):
    def __init__(self, observable_object_generator, edge_object_loader=EdgeObject):
        super(IndicatorBuilderPatch, self).__init__(observable_object_generator, edge_object_loader=EdgeObject)

    @staticmethod
    def test_mechanism_from_draft(test_mechanism):
        if test_mechanism['type'] == 'Snort':
            return SnortTestMechanism.from_dict(test_mechanism)
        if test_mechanism['type'] == 'Yara':
            return YaraTestMechanism.from_dict(test_mechanism)

    def publish_indicator(self, indicator_data, user):
        indicator = DBIndicator(
            id_=indicator_data['id'],
            title=indicator_data.get('title'),
            description=indicator_data.get('description'),
            short_description=indicator_data.get('short_description'),
        )
        indicator.add_indicator_type(indicator_data.get('indicatorType'))
        indicator.confidence = indicator_data.get('confidence', '')
        indicator.id_ns = indicator_data.get('id_ns', '')
        ident = EdgeIdentity(name=indicator_data.get('producer', ''))
        indicator.producer = EdgeInformationSource(identity=ident)
        indicator.handling = handling_from_draft('ind', indicator_data)

        if 'test_mechanisms' in indicator_data:
            for test_mechanism in indicator_data['test_mechanisms']:
                indicator.test_mechanisms.append(IndicatorBuilderPatch.test_mechanism_from_draft(test_mechanism))


        api_objects = {}
        observable_composition = ObservableComposition(operator=indicator_data.get('composition_type'))

        # If this is an Update rather than a create,
        #  we only need to copy the id and ns to the composition
        reedit_flag = 0

        # New Observables via Build or Edit
        for data in indicator_data['observables']:
            observable_id = data.get('id')
            if observable_id is None:
                # No id for this observable, therefore it is new and must be created:
                object_type = data['objectType']
                object_type_info = self.observable_object_generator.get_object_type_information(object_type)
                observable_object = self.observable_object_generator.generate_observable_object_from_data(object_type,
                                                                                                          data)

                object_container = Object(observable_object)
                object_container.id_ = self.generate_id(object_type_info['id_prefix'])

                # Create the observable, and store it in a collection so they can be saved to the database later on:
                observable_id = self.generate_id('observable')
                observable = Observable(
                    title=data['title'],
                    description=data.get('description', ''),
                    item=object_container,
                    id_=observable_id)
                observable.id_ns = indicator_data['id_ns']
                api_objects[observable.id_] = ApiObject('obs', observable)
            elif reedit_flag == 0 and self._is_re_edit_mode(data):
                reedit_flag = 1

            # Create a reference to the observable, and add it to the observable composition.
            # The observable composition will be added to the indicator.
            # Adding references to the composition saves duplication of data.
            observable_reference = Observable(idref=observable_id, idref_ns=indicator_data['id_ns'])
            observable_composition.add(observable_reference)

        # For some reason, the observable composition must be wrapped up in another observable.
        # So to clarify, at this point, we have an observable that contains an observable composition. This composition
        # contains a collection of references to the actual observables.

        # We only want a new ID for the observable composition (obs) if it is first-time Build
        #  otherwise, get it from...?the database?
        if reedit_flag:
            user_action_log = logging.getLogger('user_actions')
            user_action_log.info("%s updated STIX item %s (%s)", user.username, indicator.id_, indicator.title)
        # EOIndicator = self.edge_object_loader.load(indicator.id_)              # Get the parent indicator
        #     find_ob_comp = lambda edges: [x.fetch() for x in edges if x.ty == 'obs'][0]
        #     # Find the observable composition among it's edges and return only the first hit.
        #     # The call to fetch() resolves the idref into an instance of the object itself
        #     existing_obs_comp = find_ob_comp(EOIndicator.edges)
        #     parent_observable = Observable(item=observable_composition, id_=existing_obs_comp.id_)
        # else:
        parent_observable = Observable(item=observable_composition, id_=self.generate_id('observable'))

        parent_observable.id_ns = indicator.id_ns
        parent_observable.timestamp = datetime.utcnow()  # needed for versioning Observable Composition

        # ...and store this observable so we can actually write its contents to the database later...
        api_objects[parent_observable.id_] = ApiObject('obs', parent_observable)

        # Add a reference of the 'parent' observable to the indicator
        parent_observable_reference = Observable(idref=parent_observable.id_, idref_ns=indicator.id_ns)
        indicator.add_observable(parent_observable_reference)

        indicator_api_object = ApiObject('ind', indicator)
        # Process related items/correlations
        [relate.correlateIndtoTtp(indicator_api_object, item['idref']) for item in
         indicator_data.get('indicated_ttps', [])]
        [relate.correlateIndtoInd(indicator_api_object, item['idref']) for item in
         indicator_data.get('related_indicators', [])]
        [relate.correlateIndtoCoa(indicator_api_object, item['idref']) for item in
         indicator_data.get('suggested_coas', [])]
        # Store the indicator so we can write it to the database later
        api_objects[indicator_api_object.id_] = indicator_api_object

        # Finally lets add everything to our Mongo collection...
        tlp = (indicator_data.get('tlp') or 'NULL').upper()
        esms = lines2list(indicator_data.get('markings', ""))

        inbox_processor = InboxProcessorForBuilders(
            user=user,
            trustgroups=indicator_data.get('trustgroups', []),
        )
        for api_obj in api_objects.itervalues():
            inbox_processor.add(InboxItem(api_object=api_obj,
                                          etlp=tlp,
                                          esms=esms))
        inbox_processor.run()

        self.delete_draft(user, indicator_data['id'])

def apply_patch():
    WHICH_DBOBJ['ind'] = DBIndicatorPatch
    IndicatorBuilder.publish_indicator = IndicatorBuilderPatch(CERTObservableObjectGenerator()).publish_indicator
