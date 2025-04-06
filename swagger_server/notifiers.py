
from swagger_server.models.notification import Notification  # noqa: E501
from swagger_server import mqtt
from config import NOTIFIER_BINDINGS

def dispatch(resourceName, operation, subscriptionObj):
    """
    Dispatch notifications to supported bindings
    Currently WEBHOOK notifications handled seperately, so not considered/handled here.
    """
    if operation == 'READ':
        # Non WEBHOOK notifiers don't support READ, because they are not useful
        return

    AVAILABLE_NOTIFIER_BINDINGS = NOTIFIER_BINDINGS.copy()
    if 'WEBHOOK' in AVAILABLE_NOTIFIER_BINDINGS:
        AVAILABLE_NOTIFIER_BINDINGS.remove('WEBHOOK')

    if NOTIFIER_BINDINGS:
        # There is at least one binding, so instantiate the notification
        notification = Notification(object_type=resourceName,
                                    operation=operation,
                                    targets=None, # TODO: We need to deal with targets for object privacy!
                                    object=subscriptionObj)
        notification_dict = notification.to_dict()
    else:
        return
    # There is at least one binding, so dispatch on each
    for binding in AVAILABLE_NOTIFIER_BINDINGS:
        if binding == 'MQTT':
            mqtt.notification(resourceName, operation, notification_dict)
        # TODO: Dispatch on other bindings here
    return
