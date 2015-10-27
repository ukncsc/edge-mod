
from edge.generic import WHICH_DBOBJ
from edge.indicator import DBIndicator
from edge.tools import rgetattr


class DBIndicatorPatch(DBIndicator):

    def __init__(self, obj=None, id_=None, idref=None, timestamp=None, title=None, description=None, short_description=None):
        super(DBIndicatorPatch, self).__init__(obj, id_, idref, timestamp, title, description, short_description)

    @classmethod
    def to_draft(cls, indicator, tg, load_by_id, id_ns=''):
        draft = super(DBIndicatorPatch, cls).to_draft(indicator, tg, load_by_id, id_ns)
        kill_chain_phases = rgetattr(indicator, ['kill_chain_phases'])
        if kill_chain_phases:
            draft['kill_chain_phase'] = rgetattr(kill_chain_phases[0], ['phase_id'], '')
        return draft

WHICH_DBOBJ['ind'] = DBIndicatorPatch
