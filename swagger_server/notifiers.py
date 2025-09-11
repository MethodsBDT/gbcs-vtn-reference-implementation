
from swagger_server.models.notification import Notification  # noqa: E501
from swagger_server import mqtt
from config import NOTIFIER_BINDINGS
import logging
from pprint import pformat
from swagger_server.globals import VENS
from typing import Any, Callable, Union, Dict, List, Set


def clean_targets(targets):
    """
    IDK why this is necesary, but without this I cannot get the tests to pass!

    Cleans and flattens a targets list for OpenADR compliance.
    Also removes duplicates while preserving order.
    Example
      targets = ["group1", ["group1"], ["group1"], "group2", ["group2", "group3"]]
      cleaned = clean_targets(targets)
      print(cleaned)  # ['group1', 'group2', 'group3']
    """
    if not isinstance(targets, list):
        return []

    flattened = []
    seen = set()

    def flatten(item):
        if isinstance(item, list):
            for subitem in item:
                flatten(subitem)
        elif isinstance(item, str) and item not in seen:
            flattened.append(item)
            seen.add(item)

    for item in targets:
        flatten(item)

    return flattened


def get_targets(notification_object: Dict) -> Set:
    """
    .get(targets) often returns None, so this is a workaround
    """
    targets = clean_targets(notification_object.get('targets', None))
    logging.debug(f"reason=getTargets,targets={targets}")
    if targets:
        return set(targets)
    else:
        return set()


def ven_tracker(resource_name: str, operation: str, notification: Dict):
    """
    Maintains dict of VENS
    Note: Presumably there is a way to use the Object Store here instead of this, but "whatever"
    """
    if (operation is None) or (operation == 'READ'):
        return
    notification_object = notification.get('object', None)
    if notification_object is None:
        # This should not happen
        return
    if resource_name == 'VEN':
        ven_id = notification_object.get('id', None)
        ven_name = notification_object.get('ven_name', None)
        client_id = notification_object.get('client_id', None)
        targets = get_targets(notification_object)
        if ven_id and ((operation == "CREATE") or (operation == "UPDATE")):
            # If this is an UPDATE, we need to preserve any resources
            record = VENS.get(ven_id, {})
            record.update({'id': ven_id,
                           'name': ven_name,
                           'client_id': client_id,
                           'targets': targets})
            VENS.update({ven_id: record})
        elif ven_id and (operation == "DELETE"):
            # TODO Is removing a ven on DELETE correct?  TBD...
            VENS.pop(ven_id, None)
    elif resource_name == 'RESOURCE':
        resource_id = notification_object.get('id', None)
        ven_id = notification_object.get('ven_id', None)
        targets = get_targets(notification_object)
        if (operation == "CREATE") or (operation == "UPDATE"):
            if resource_id and ven_id:
                ven_record = VENS.get(ven_id, {})
                ven_record.update({'resources':
                                   {resource_id: {'id': resource_id,
                                                  'targets': targets}}})
                VENS.update({ven_id: ven_record})
        elif ven_id and resource_id and (operation == "DELETE"):
            ven_record = VENS.get(ven_id, None)
            if ven_record:
                ven_resources = ven_record.get('resources',{})
                ven_resources.pop(resource_id, None)
                ven_record.update({'resources': ven_resources})
                VENS.update({ven_id: ven_record})
            else:
                logging.debug(f"reason=venTrackerResourceNotInVen,resourceID={resource_id},vensID={ven_id}")
    logging.debug(f"reason=venTracker,operation={operation},vens=\n{pformat(VENS)}")


def ven_and_resource_targets(ven_id: str) -> Set:
    """
    Returns a the set union of the ven's targets and the targets of all resources of the venID
    """
    ven_record = VENS.get(ven_id, None)
    if ven_record is None:
        return set()
    ven_targets = get_targets(ven_record).copy()
    ven_resources = ven_record.get('resources', {})
    for resource_record in ven_resources.values():
        resource_targets = resource_record.get('targets', set())
        ven_targets.update(resource_targets)
    return ven_targets


def resolve_ven_ids_from_targets(targets_list: List) -> Set:
    """
    Returns a set containing the ven.id of each ven that has been assigned one of the targets
    """
    result = set()
    targets = set(targets_list)
    if not targets:
        return result
    for ven_id in VENS.keys():
        if targets.intersection(ven_and_resource_targets(ven_id)):
            # At least one of the targets for the ven with this ven_id are contained within the targets
            result.update(ven_id)
    return result


def dispatch(resource_name, operation, vtn_object):
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
        notification = Notification(object_type=resource_name,
                                    operation=operation,
                                    # TODO TBD if this is correct
                                    targets=getattr(vtn_object, 'targets', None),
                                    object=vtn_object)
        notification_dict = notification.to_dict()
    else:
        return
    logging.debug(f"reason=dispatch,object:\n{pformat(notification_dict)}")
    # Dispatch on each notififer binding
    for binding in AVAILABLE_NOTIFIER_BINDINGS:
        if binding == 'MQTT':
            if (resource_name == 'VEN') or (resource_name == 'RESOURCE'):
                ven_tracker(resource_name, operation, notification_dict)
            mqtt.notification(resource_name, operation, notification_dict)
        # TODO: Dispatch on other bindings here
    return
