
from users.decorators import json_body, login_required_ajax, superuser_or_staff_role
from adapters.certuk_mod.cron.purge_job import update as purge_update
from adapters.certuk_mod.cron.purge_job import task_is_running as purge_task_is_running

from adapters.certuk_mod.cron.fts_job import update as fts_update
from adapters.certuk_mod.cron.fts_job import task_is_running as fts_task_is_running
from adapters.certuk_mod.cron.dedup_job import update as dedup_update
from adapters.certuk_mod.cron.dedup_job import task_is_running as dedup_task_is_running
from adapters.certuk_mod.cron.backlinks_job import task_is_running as bl_task_is_running
from adapters.certuk_mod.cron.backlinks_job import update as bl_update

@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_get_purge_task_status(request, data):
    return {
        'status': purge_task_is_running()
    }


@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_run_purge(request, data):
    task = purge_update.delay()
    return {
        'id': task.id
    }

@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_get_fts_task_status(request, data):
    return {
        'status': fts_task_is_running()
    }


@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_run_fts(request, data):
    task = fts_update.delay()
    return {
        'id': task.id
    }


@login_required_ajax
@superuser_or_staff_role
@json_body

def ajax_get_dedup_task_status(request, data):
    return {
        'status': dedup_task_is_running()
    }


@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_run_dedup(request, data):
    task = dedup_update.delay()

def ajax_get_mod_bl_task_status(request, data):
    return {
        'status': bl_task_is_running()
    }

@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_run_bl(request, data):
    task = bl_update.delay()
    return {
        'id': task.id
    }
