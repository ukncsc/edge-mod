import unittest
import mock
import datetime
import pytz
from dateutil import parser as dt_parser
from adapters.certuk_mod.timeline.views import ajax_incident_timeline
from django.conf import settings

class IncidentTimelineTests(unittest.TestCase):
    @mock.patch('adapters.certuk_mod.timeline.views.EdgeObject')
    @mock.patch('django.http.request.HttpRequest')
    def test_timezones(self, mock_request, mock_EdgeObject):

        mock_eo_instance = mock.MagicMock()

        date = "01-01-2016T10:11:12+0000"
        date_ms = (dt_parser.parse(date).astimezone(settings.LOCAL_TZ)
                   - datetime.datetime(1970, 1, 1).replace(tzinfo=settings.LOCAL_TZ))\
                      .total_seconds() * 1000.0
        mock_eo_instance.obj.time.to_dict.return_value = {'first_malicious_action': date,
                                                          'initial_compromise': "01-01-2016T11:11:12+0100",
                                                          'first_data_exfiltration': {'value':date}}
        mock_eo_instance.ty = "inc"
        mock_EdgeObject.load.return_value = mock_eo_instance

        class mockJsonResponse:
            def __init__(self, *args, **kwargs):
                self.graph = args[0]

        with mock.patch('adapters.certuk_mod.timeline.views.JsonResponse', mockJsonResponse):
            response = ajax_incident_timeline(mock_request, "pss:inc-4e0307e4-3e7c-43c0-b7e8-a998d94906e5")

        assert (len(response.graph['nodes']) == 3)
        for node in response.graph['nodes']:
            assert (node['date'] == date_ms)

