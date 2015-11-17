
from datetime import datetime
import traceback
from mongoengine import DoesNotExist
from activity.models import StixActivityAction
from crashlog import models as crash_log
from users.models import Repository_User
import status


APP_NAME = 'adapters/publisher'


def create_action_if_not_exist(action_name):
    try:
        StixActivityAction.objects.get(description=action_name)
    except DoesNotExist:
        admin_user = Repository_User.objects.get(username='admin')
        action = StixActivityAction(
            entered_by=admin_user.id,
            updated_by=admin_user.id,
            updated_on=datetime.utcnow(),
            is_active=True,
            description=action_name,
        )
        action.save()


def log_error(e, message=''):
    stack_trace = traceback.format_exc()
    crash_log.save(APP_NAME, message + ': ' + str(e), stack_trace)


def configure_publisher_actions():
    try:
        create_action_if_not_exist(status.PUBLISH_SUCCESS)
        create_action_if_not_exist(status.PUBLISH_FAIL)
    except Exception, e:
        log_error(e)
