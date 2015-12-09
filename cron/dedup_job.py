#!/usr/bin/env python2.7

import os
import sys
import subprocess
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repository.settings')
from django.conf import settings
if not hasattr(settings, 'BASE_DIR'):
    raise Exception("Failed to import Django settings")
from celery import Celery
app = Celery('caches', config_source='repository.celeryconfig')
from edge import LOCAL_ALIAS
from edge.generic import EdgeObject, EdgeError
from edge.inbox import InboxItem, InboxProcessorForBuilders
from edge.tools import FileLockOrFail, CannotLock
from crashlog import models as crashlog
from mongoengine.connection import get_db
from users.models import Repository_User


LOCAL_ALIAS_REGEX = '^%s:' % LOCAL_ALIAS
LOCKNAME = os.path.join(settings.LOCK_DIR, 'dedup_job.lock')


def find_duplicates(db, type_):
    return db.stix.aggregate([
        {
            '$match': {
                '_id': {
                    '$regex': LOCAL_ALIAS_REGEX
                },
                'type': type_
            }
        },
        {
            '$sort': {
                'created_on': -1
            }
        },
        {
            '$group': {
                '_id': '$data.hash',
                'uniqueIds': {
                    '$addToSet': '$_id'
                },
                'count': {'$sum': 1}
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}
            }
        }
    ], cursor={})


def build_maptable(master, dups):
    return {dup: master for dup in dups}


def find_parents(db, id_):
    for backlink in db.stix_backlinks.find({r'_id': id_}):
        for backlink_value in backlink.get(r'value'):
            yield backlink_value


def cleanup_ind(to_save_objs, ind):
    pass


def get_sighting_count(obs):
    sighting_count = getattr(obs, 'sighting_count', 1)
    if sighting_count is None:
        sighting_count = 1
    return sighting_count


def cleanup_obs(to_save_objs, obs):
    composition = obs.obj.observable_composition
    if composition is not None:
        all_refs = getattr(composition, 'observables', [])
        if len(all_refs) > 1:
            seen_ids = {}
            for ref in all_refs:
                idref = ref.idref
                if idref in seen_ids:
                    _, api_object = seen_ids[idref]
                    api_object.obj.sighting_count = get_sighting_count(api_object.obj) + get_sighting_count(ref)
                else:
                    api_object = EdgeObject.load(idref).to_ApiObject()
                    seen_ids[idref] = (ref, api_object)
                    to_save_objs.add(api_object)
            composition.observables = [ref for ref, _ in seen_ids.itervalues()]
            to_save_objs.add(obs)


def cleanup_ttp(to_save_objs, ttp):
    pass


CLEANUP_DISPATCH = {
    'ind': cleanup_ind,
    'obs': cleanup_obs,
    'ttp': cleanup_ttp,
}


def resave(edge_object, api_objects):
    inbox_processor = InboxProcessorForBuilders(
        user=Repository_User.objects.get(username=getattr(edge_object, 'created_by_username', 'admin'))
    )
    for api_object in api_objects:
        inbox_processor.add(InboxItem(
            api_object=api_object,
            etlp=edge_object.etlp,
            etou=edge_object.etou,
            esms=edge_object.esms
        ))
    inbox_processor.run()


def deduplicate(db, master, dups):
    print "====\n%s: %s" % (master, dups)
    maptable = build_maptable(master, dups)
    for dup in dups:
        for parent in find_parents(db, dup):
            try:
                edge_object = EdgeObject.load(parent)
                api_object = edge_object.to_ApiObject()
                new_api_obj = api_object.remap(maptable)
                to_save = set()
                CLEANUP_DISPATCH[edge_object.ty](to_save, new_api_obj)
                if len(to_save) > 0:
                    resave(edge_object, to_save)
            except EdgeError as e:
                print "Couldn't find %s" % parent
    db.stix.remove({'_id': {'$in': dups}})
    db.stix_backlinks.remove({'_id': {'$in': dups}})


@app.task(ignore_result=True, queue='mapreduce')
def update(force_start=False):
    try:
        with FileLockOrFail(LOCKNAME):
            return update_main(force_start)
    except CannotLock:
        return 0


def update_main(force_start=False):
    try:
        db = get_db()
        duplicates = find_duplicates(db, 'obs')
        for duplicate in duplicates:
            unique_ids = duplicate.get('uniqueIds')
            deduplicate(db, unique_ids[0], unique_ids[1:])
    except subprocess.CalledProcessError as e:
        crash_message = '\n'.join([
            'returncode=%d' % e.returncode,
            'output:\n%s' % e.output
        ])
        crashlog.save('dedup_job', 'CalledProcessError', crash_message)
        raise

    return 0


def main():
    rc = update()
    sys.exit(rc)


if __name__ == '__main__':
    main()
