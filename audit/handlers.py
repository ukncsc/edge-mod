
from activity.models import StixActivityEntry, StixActivityAction


def log_activity(source, **event_args):
    action = StixActivityAction.objects.get(description=event_args['publish_status'])
    activity_entry = StixActivityEntry(
        entered_by=event_args['user'].id,
        entered_by_username=event_args['user'].username,
        stix_id=event_args['stix_id'],
        action_id=action.id,
        action_description=action.description,
        note=event_args['message']
    )
    activity_entry.save()
