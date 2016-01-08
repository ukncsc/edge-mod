
from datetime import datetime
from mongoengine import DoesNotExist
from activity.models import StixActivityAction
from users.models import Repository_User
import status
from adapters.certuk_mod.common.logger import log_error


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


def configure_publisher_actions():
    try:
        create_action_if_not_exist(status.PUBLISH_SUCCESS)
        create_action_if_not_exist(status.PUBLISH_FAIL)
    except Exception, e:
        log_error(e, 'adapters/audit/setup')
