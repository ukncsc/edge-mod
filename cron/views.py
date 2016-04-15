
from users.decorators import json_body, login_required_ajax, superuser_or_staff_role
from adapters.certuk_mod.cron.purge_job import update, task_is_running


@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_get_purge_task_status(request, data):
    return {
        'status': task_is_running()
    }


@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_run_purge(request, data):
    task = update.delay()
    return {
        'id': task.id
    }

@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_get_fts_status(request, data):
    return {
        'status': task_is_running()
    }


@login_required_ajax
@superuser_or_staff_role
@json_body
def ajax_run_fts(request, data):
    task = update.delay()
    return {
        'id': task.id
    }
