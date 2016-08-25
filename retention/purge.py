import os
from time import sleep

from celery.exceptions import TimeoutError
from edge import LOCAL_NAMESPACE, LOCAL_ALIAS
from mongoengine.connection import get_db
from datetime import datetime
from dateutil.relativedelta import relativedelta
from repository.scheduler import PeriodicTaskWithTTL
from edge.tools import StopWatch
from adapters.certuk_mod.common.activity import save as log_activity


class STIXPurge(object):
    PAGE_SIZE = 2000

    def __init__(self, retention_config):
        self.retention_config = retention_config

    def _get_old_ids(self, minimum_id, minimum_date, version_epoch, namespace_filter):
        old_external_ids = get_db().stix.find({
            'created_on': {
                '$lt': minimum_date
            },
            'type': {'$in': ['obs', 'ind']},
            '_id': {
                '$gt': minimum_id
            },
            'data.idns': namespace_filter,
            'data.summary.type': {
                # Exclude Observable Compositions, since they will only ever have at most 1 back link
                # We sweep up any orphaned Observable Compositions later...
                '$ne': 'ObservableComposition'
            },
            'cv': {
                '$lte': str(version_epoch)
            }
        }, {
            '_id': 1,
            'created_on': 1
        }).sort([('created_on', -1), ('_id', 1)]).limit(self.PAGE_SIZE)

        old_external_ids = list(old_external_ids)
        if not old_external_ids:
            return None, None, []
        new_minimum_date = old_external_ids[-1]['created_on']
        # We need this, just in case we have more than PAGE_SIZE worth of data with the same 'created_on' date.
        # If not, we'd end up in a loop because the returned new_minimum_date is not updated.
        # We could simply sort on '_id' only, however it's probably quicker to sort on a date field first, then by ID.
        new_minimum_id = old_external_ids[-1]['_id']

        old_external_ids = [doc['_id'] for doc in old_external_ids]

        return new_minimum_id, new_minimum_date, old_external_ids

    @staticmethod
    def __get_back_links_filter_where_clause(minimum_back_links):
        with open(os.path.join(os.path.dirname(__file__), 'back-links-filter.js')) as _file:
            where_clause = _file.read()
            return where_clause.replace('excludePackages', '').replace('minimumBackLinks', str(minimum_back_links))

    @staticmethod
    def _get_items_under_link_threshold(ids_to_search, minimum_back_links):
        over_threshold_query = {
            '_id': {
                '$in': ids_to_search
            },
            # There's no easy way of getting the length of an object in Mongo,
            # so we need a $where clause which uses JavaScript... :(
            # Note that if an item exists in stix_backlinks, then it will have
            # at least one entry in value
            '$where': STIXPurge.__get_back_links_filter_where_clause(minimum_back_links)
        }

        over_link_threshold_ids = get_db().stix_backlinks.find(over_threshold_query, {
            '_id': 1
            # stix_backlinks doesn't contain the hash unfortunately...
        })
        over_link_threshold_ids = [doc['_id'] for doc in over_link_threshold_ids]

        if len(ids_to_search) == len(over_link_threshold_ids):
            return {}

        under_link_threshold_ids = list(set(ids_to_search) - set(over_link_threshold_ids))

        under_link_threshold_objects = get_db().stix.find({
            '_id': {
                '$in': under_link_threshold_ids
            }
        }, {
            '_id': 1,
            'data.hash': 1
        })
        under_link_threshold_objects = {doc['_id']: doc['data']['hash'] for doc in under_link_threshold_objects}

        return under_link_threshold_objects

    def _get_hashes_for_possible_deletion(self, qualifying_hashes, namespace_filter):
        # Only take the sightings count for objects that are in the same namespace
        hash_counts = get_db().stix.aggregate([
            {
                '$match': {
                    'data.hash': {
                        '$in': qualifying_hashes
                    },
                    'data.idns': namespace_filter
                }
            },
            {
                '$group': {
                    '_id': '$data.hash',
                    'sightings': {
                        '$sum': {
                            '$cond': [
                                '$data.api.sighting_count',
                                '$data.api.sighting_count',
                                1
                            ]
                        }
                    }
                }
            },
            {
                '$match': {
                    'sightings': {
                        '$lt': self.retention_config.minimum_sightings
                    }
                }
            }
        ], cursor={})

        hashes = [doc['_id'] for doc in hash_counts]

        return hashes

    def _get_ids_for_deletion(self, hashes_lt_min_sightings, ids_old_ext_no_back_links, namespace_filter):
        query = {
            'data.hash': {
                '$in': hashes_lt_min_sightings
            },
            'data.idns': namespace_filter
        }
        # If we are deleting things with more than 1 hash-based sighting, then we must filter by id too, otherwise we
        #  risk deleting items that are from our namespace/have back links/aren't old etc...
        if (self.retention_config.minimum_sightings - 1) > 1:
            query.update({
                '_id': {
                    '$in': ids_old_ext_no_back_links
                },
            })

        ids_to_delete = get_db().stix.find(query, {
            '_id': 1
        })

        return [doc['_id'] for doc in ids_to_delete]

    @staticmethod
    def _get_orphaned_external_observable_compositions(as_at_timestamp):
        composition_ids = get_db().stix.find({
            'data.summary.type': 'ObservableComposition',
            'created_on': {
                '$lt': as_at_timestamp
            }
        }, {
            '_id': 1
        })
        composition_ids = [doc['_id'] for doc in composition_ids]
        orphaned_ids = []

        for page_index in range(0, len(composition_ids), STIXPurge.PAGE_SIZE):
            chunk_ids = composition_ids[page_index: page_index + STIXPurge.PAGE_SIZE]
            with_back_links_chunk = get_db().stix_backlinks.find({
                '_id': {
                    '$in': chunk_ids
                }
            }, {
                '_id': 1
            })
            orphaned_ids += list(set(chunk_ids) - set([doc['_id'] for doc in with_back_links_chunk]))

        return orphaned_ids

    def get_purge_candidates(self, minimum_date, namespace_filter):
        version_epoch = int(1000 * (minimum_date - datetime(1970, 1, 1)).total_seconds() + 0.5)
        minimum_id = ''

        ids_to_delete = []
        while True:
            minimum_id, minimum_date, old_ids = self._get_old_ids(minimum_id, minimum_date,
                                                                           version_epoch, namespace_filter)

            if not old_ids:
                break

            items_under_link_threshold = self._get_items_under_link_threshold(old_ids,
                                                                              self.retention_config.minimum_back_links)

            if not items_under_link_threshold:
                continue

            hashes_deletion_candidates = self._get_hashes_for_possible_deletion(items_under_link_threshold.values(), namespace_filter)

            ids_to_delete += self._get_ids_for_deletion(hashes_deletion_candidates, items_under_link_threshold.keys(), namespace_filter)

        return ids_to_delete

    @staticmethod
    def remove(ids):
        if not ids:
            return

        get_db().stix_backlinks.remove({
            '_id': {
                '$in': ids
            }
        })
        edges_cursor = get_db().stix.find({
            '_id': {
                '$in': ids
            }
        }, {
            '_id': 1,
            'data.edges': 1
        })

        ids_with_edges = {}
        for doc in edges_cursor:
            doc_edges = doc.get('data', {}).get('edges', {})
            if doc_edges:
                ids_with_edges[doc['_id']] = [edge_id for edge_id in doc_edges]

        if ids_with_edges:
            bulk_operation = get_db().stix_backlinks.initialize_unordered_bulk_op()
            for parent_id in ids_with_edges:
                bulk_operation.find({
                    '_id': {
                        '$in': ids_with_edges[parent_id]
                    }
                }).update({
                    '$unset': {
                        'value.%s' % parent_id: 1
                    }
                })
            bulk_operation.execute()

        # Un-setting some back link values may result in entries which are empty...
        get_db().stix_backlinks.remove({
            'value': {
                '$eq': {

                }
            }
        })

        get_db().stix.remove({
            '_id': {
                '$in': ids
            }
        })


    @staticmethod
    def wait_for_background_jobs_completion(as_at_date, minutes_to_wait=5, poll_interval=5):
            tries_remaining = int((60 * minutes_to_wait) / poll_interval)
            while tries_remaining:
                cache_sightings = PeriodicTaskWithTTL.objects.get(name='cache_sightings')
                cache_backlinks = PeriodicTaskWithTTL.objects.get(name='cache_backlinks')
                if cache_backlinks.last_run_at > as_at_date and cache_sightings.last_run_at > as_at_date:
                    return
                else:
                    sleep(poll_interval)
                    tries_remaining -= 1
            raise TimeoutError('Timeout waiting for sightings and backlinks jobs to complete.  Will retry in 24 hours.')

    def run(self):
        def build_activity_message(min_date, objects, compositions, time_ms):
            def summarise(into, summary_template, items):
                num_items = len(items)
                into.append(summary_template % num_items)

            namespace_filter_text = 'in %s namespace,' % LOCAL_ALIAS.upper()
            if not self.retention_config.only_local_ns:
                namespace_filter_text = 'not in %s namespace,' % LOCAL_ALIAS.upper()

            messages = [
                'Objects created before %s which are %s are candidates for deletion' % (min_date.strftime("%Y-%m-%d %H:%M:%S"), namespace_filter_text)]
            summarise(messages, 'Found %d objects with insufficient back links or sightings', objects)
            summarise(messages, 'Found %d orphaned observable compositions', compositions)
            messages.append('In %dms' % time_ms)
            return "\n".join(messages)

        namespace_filter = LOCAL_NAMESPACE
        if not self.retention_config.only_local_ns:
            namespace_filter = {'$ne': LOCAL_NAMESPACE}

        timer = StopWatch()
        try:
            current_date = datetime.utcnow()
            STIXPurge.wait_for_background_jobs_completion(current_date)
            minimum_date = current_date - relativedelta(months=self.retention_config.max_age_in_months)

            # Get old items that don't have enough back links and sightings (excluding observable compositions):
            objects_to_delete = self.get_purge_candidates(minimum_date, namespace_filter)
            # Look for any observable compositions that were orphaned on the previous call to run:
            orphaned_observable_compositions_to_delete = STIXPurge._get_orphaned_external_observable_compositions(
                current_date)

            ids_to_delete = objects_to_delete + orphaned_observable_compositions_to_delete

            for page_index in range(0, len(ids_to_delete), self.PAGE_SIZE):
                try:
                    chunk_ids = ids_to_delete[page_index: page_index + self.PAGE_SIZE]
                    STIXPurge.remove(chunk_ids)
                except Exception as e:
                    log_activity('system', 'AGEING', 'ERROR', e.message)
        except Exception as e:
            log_activity('system', 'AGEING', 'ERROR', e.message)
        else:
            log_activity('system', 'AGEING', 'INFO', build_activity_message(
                minimum_date, objects_to_delete, orphaned_observable_compositions_to_delete,
                timer.ms()
            ))
