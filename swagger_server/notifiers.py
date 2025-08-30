
from swagger_server.models.notification import Notification  # noqa: E501
from swagger_server import mqtt
from config import NOTIFIER_BINDINGS
import logging
from pprint import pformat

def dispatch(resourceName, operation, vtn_object):
    """
    Dispatch notifications to supported bindings
    Currently WEBHOOK notifications handled seperately, so not considered/handled here.
    """
    if (operation is None) or (operation == 'READ'):
        # Non WEBHOOK notifiers don't support READ, because they are not useful
        # If operation is None, nothing to do
        return

    AVAILABLE_NOTIFIER_BINDINGS = NOTIFIER_BINDINGS.copy()
    if 'WEBHOOK' in AVAILABLE_NOTIFIER_BINDINGS:
        AVAILABLE_NOTIFIER_BINDINGS.remove('WEBHOOK')

    if NOTIFIER_BINDINGS:
        # There is at least one binding, so instantiate the notification
        notification = Notification(object_type=resourceName,
                                    operation=operation,
                                    # TODO TBD if this is correct
                                    targets=getattr(vtn_object, 'targets', None),
                                    object=vtn_object)
        notification_dict = notification.to_dict()
    else:
        return
    # TODO FIXME change to debug before merge
    logging.info(f"reason=dispatch,object={pformat(notification_dict)}")
    # Dispatch on each notififer binding
    for binding in AVAILABLE_NOTIFIER_BINDINGS:
        if binding == 'MQTT':
            mqtt.notification(resourceName, operation, notification_dict)
        # TODO: Dispatch on other bindings here
    return
