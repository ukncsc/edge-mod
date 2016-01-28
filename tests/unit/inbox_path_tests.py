import unittest
import mock
from adapters.certuk_mod.patch import inbox_patch
from dateutil.parser import parse as date_time_parse


class InboxPatchTests(unittest.TestCase):

    @mock.patch('adapters.certuk_mod.publisher.publisher_config.get_db', autospec=True)
    def test_update_non_observables(self, mock_db):

        mock_objects = {
           "PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515": {
               "_id": "PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515",
               "created_on": {
                  "$date": "2015-09-07T10:45:14.381Z"
               },
               "data": {
                  "api": {
                     "timestamp": "2015-09-07T10:45:14.291293+00:00",
                  },
                  "summary": {
                     "type": [
                        "IP Watchlist"
                     ]
                  }
               },
               "type": "ind"
            }
        }

        inbox_patch.update_non_observables(mock_objects, mock_db)

        expected_date = date_time_parse("2015-09-07T10:45:14.291293+00:00")
        expected_date = (expected_date - expected_date.tzinfo.utcoffset(expected_date)).replace(tzinfo=None)

        self.assertEqual(mock_objects["PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515"]['created_on'], expected_date)
        mock_db.assert_called_with()

    @mock.patch('adapters.certuk_mod.publisher.publisher_config.get_db', autospec=True)
    def test_update_observables(self, mock_db):

        mock_top_level_objects = {
           "PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515": {
               "_id": "PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515",
               "created_on": {
                  "$date": "2015-09-02T10:45:14.381Z"
               },
               "data": {
                  "api": {
                     "timestamp": "2015-09-07T10:45:14.291293+00:00",
                  },
                  "summary": {
                     "type": [
                        "IP Watchlist"
                     ]
                  },
                  "edges": {
                     "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17": "obs"
                  }
               },
               "type": "ind"
            }
        }

        mock_observables = {
           "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17": {
               "_id": "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17",
               "created_on": {
                  "$date": "2015-09-07T14:35:04.203Z"
               },
               "data": {
                  "api": {
                     "timestamp": "2015-09-07T10:45:14.291293+00:00",
                  },
                  "summary": {
                     "type": [
                        "AddressObjectType"
                     ]
                  },
                  "edges": {
                  }
               },
               "type": "obs"
            }
        }

        inbox_patch.update_observables(mock_top_level_objects, mock_observables, mock_db)

        self.assertEqual(mock_observables["fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17"]['created_on'],
                         mock_top_level_objects["PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515"]['created_on'])
        mock_db.assert_called_with()

    @mock.patch('adapters.certuk_mod.publisher.publisher_config.get_db', autospec=True)
    def test_update_multiple_child_observables(self, mock_db):

        mock_top_level_objects = {
           "PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515": {
               "_id": "PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515",
               "created_on": {
                  "$date": "2015-09-02T10:45:14.381Z"
               },
               "data": {
                  "api": {
                     "timestamp": "2015-09-07T10:45:14.291293+00:00",
                  },
                  "summary": {
                     "type": [
                        "IP Watchlist"
                     ]
                  },
                  "edges": {
                     "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17": "obs"
                  }
               },
               "type": "ind"
            }
        }

        mock_observables = {
           "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17": {
               "_id": "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17",
               "created_on": {
                  "$date": "2015-09-07T14:35:04.203Z"
               },
               "data": {
                  "api": {
                     "timestamp": "2015-09-07T10:45:14.291293+00:00",
                  },
                  "summary": {
                     "type": [
                        "AddressObjectType"
                     ]
                  },
                  "edges": {
                      "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17joe": "obs"
                  }
               },
               "type": "obs"
            },
              "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17joe": {
               "_id": "fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17joe",
               "created_on": {
                  "$date": "2015-09-07T14:35:04.203Z"
               },
               "data": {
                  "api": {
                     "timestamp": "2015-09-07T10:45:14.291293+00:00",
                  },
                  "summary": {
                     "type": [
                        "AddressObjectType"
                     ]
                  },
                  "edges": {
                  }
               },
               "type": "obs"
            }
        }

        inbox_patch.update_observables(mock_top_level_objects, mock_observables, mock_db)

        self.assertEqual(mock_observables["fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17"]['created_on'],
                 mock_top_level_objects["PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515"]['created_on'])
        self.assertEqual(mock_observables["fireeye:observable-8328d5ae-2016-4049-b9d5-ebcd60accf17joe"]['created_on'],
                 mock_top_level_objects["PurpleSecureSystems:indicator-02db75d2-77e2-4774-a219-293318051515"]['created_on'])

        mock_db.assert_called_with()

