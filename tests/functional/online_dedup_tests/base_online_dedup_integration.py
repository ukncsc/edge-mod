import os
import subprocess

import repository.test as edge_test
from adapters.certuk_mod.dedup.dedup import STIXDedup
from adapters.certuk_mod.cron.dedup_job import DedupConfiguration
from mongoengine.connection import get_db
from edge.models import StixBacklink
from edge.generic import EdgeObject

os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'


class BaseOnlineDedupFunctionalTests(edge_test.TestCase):
    fixtures = ['stix', 'schedules', 'stix_backlinks', 'user']

    def get_OnlineDedup_config(self):
        return STIXDedup(DedupConfiguration.get())

    def set_OnlineDedup_config(self, config):
        return STIXDedup(DedupConfiguration.set_from_dict(config))

    def get_Stix_Obj_Count(self, stix_id):
        return get_db().stix.find(stix_id).count()

    def child_ID_in_Parent_Edges(self, child_id, parent_id):
        return child_id in [edges.idref for edges in EdgeObject.load(parent_id).to_ApiObject().edges()]

    def parent_ID_in_Childs_Backlinks(self, child_id, parent_id):
        return parent_id in StixBacklink.objects.get(id=child_id).edges

    def OnlineDedup_validate_nothing_deduped(self):
        stix_count_before = self.get_Stix_Obj_Count({})

        _online_dedup = self.get_OnlineDedup_config()
        _online_dedup.run()

        stix_count_after = self.get_Stix_Obj_Count({})
        self.assertEquals(stix_count_before, stix_count_after)
