import connexion
from datetime import datetime
import json
import logging
import requests

from swagger_server.models.notification import Notification  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.subscription import Subscription  # noqa: E501
from swagger_server.objStore.storageInterface import objStore
from swagger_server import util

def create_subscription(body):  # noqa: E501
    """create subscription

    Create a new subscription. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Subscription
    """
    logging.info(f"create_subscription():")

    subscriptionBody = None
    if connexion.request.is_json:
        subscriptionBody = Subscription.from_dict(connexion.request.get_json())  # noqa: E501

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    subscription = Subscription(
        created_date_time=current_time,
        object_type='SUBSCRIPTION',
        client_name=subscriptionBody.client_name,
        program_id=subscriptionBody.program_id,
        object_operations=subscriptionBody.object_operations,
        targets = subscriptionBody.targets
    )

    status = objStore.insert(subscription)
    if status != 200:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_subscription(): problem={problem}")
        return problem, status

    subscription_callback("SUBSCRIPTION", "POST", subscription)

    return subscription, 200


def delete_subscription(subscription_id):  # noqa: E501
    """delete  subscription

    Delete the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: object ID of the associated subscription.
    :type subscription_id: dict | bytes

    :rtype: Subscription
    """
    logging.info(f"delete_subscription(): subscription_id={subscription_id}")

    subscription = objStore.remove("SUBSCRIPTION", subscription_id)
    if type(subscription) is not Subscription:
        status = subscription
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"delete_subscription(): problem={problem}")
        return problem, status

    subscription_callback("SUBSCRIPTION", "DELETE", subscription)

    return subscription, 200

def search_subscription_by_id(subscription_id):  # noqa: E501
    """search subscriptions by ID

    Return the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: object ID of the associated subscription.
    :type subscription_id: dict | bytes

    :rtype: Subscription
    """
    logging.info(f"search_subscription_by_id(): subscription_id={subscription_id}")

    subscription = objStore.search("SUBSCRIPTION", subscription_id)
    logging.debug(f"search_all_subscriptions(): subscription={subscription}")
    if type(subscription) is not Subscription:
        status = subscription
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_subscriptions(): problem={problem}")
        return problem, status

    subscription_callback("SUBSCRIPTION", "GET", subscription)

    return subscription, 200

def search_subscriptions(program_id=None, client_name=None, target_type=None, target_values=None, objects=None, skip=None, limit=None):  # noqa: E501
    """search subscriptions

    List all subscriptions. May filter results by programID and clientID as query params. May filter results by objects as query param. See objectTypes schema. Use skip and pagination query params to limit response size.  # noqa: E501

    :param program_id: filter results to subscriptions with programID.
    :type program_id: dict | bytes
    :param client_name: filter results to subscriptions with clientName.
    :type client_name: str
    :param target_type: Indicates targeting type, e.g. GROUP
    :type target_type: str
    :param target_values: List of target values, e.g. group names
    :type target_values: List[str]
    :param objects: list of objects to subscribe to.
    :type objects: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Subscription]
    """
    logging.info(
        f"search_all_subscriptions(): program_id={program_id} client_name={client_name} target_type={target_type} target_values={target_values} objects={objects} skip={skip} limit={limit}")

    subscriptions = objStore.search_all("SUBSCRIPTION")
    logging.debug(f"search_all_subscriptions(): subscriptions={subscriptions}")
    if type(subscriptions) is not list:
        status = subscriptions
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_subscriptions(): problem={problem}")
        return problem, status

    if program_id != None:
        # strip leading [' and tailing ']
        # program_id = program_id[2:-2]
        subscriptions = [subscription for subscription in subscriptions if subscription.program_id == program_id]
        if len(subscriptions) == 0:
            problem = Problem(title="Not Found: program_id not found", status="404")
            logging.warning(f"search_all_subscriptions(): problem={problem}")
            return problem, 404
    if client_name != None:
        # strip leading [' and tailing ']
        # client_name = client_name[2:-2]
        subscriptions = [subscription for subscription in subscriptions if subscription.client_name == client_name]
        if len(subscriptions) == 0:
            problem = Problem(title="Not Found: client_name not found", status="404")
            logging.warning(f"search_all_subscriptions(): problem={problem}")
            return problem, 404
    subscriptions = util.getTargets(subscriptions, target_type, target_values)
    subscriptions = util.getObjects(subscriptions, objects)
    if skip != None:
        if len(subscriptions) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_subscriptions(): problem={problem}")
            return problem, 404
        subscriptions = subscriptions[skip:]
    if limit != None:
        subscriptions = subscriptions[:limit]

    logging.debug(f"search_all_subscriptions(): subscriptions={subscriptions}")

    subscription_callback("SUBSCRIPTION", "GET", subscriptions)
    return subscriptions


def update_subscription(subscription_id, body=None):  # noqa: E501
    """update  subscription

    Update the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: object ID of the associated subscription.
    :type subscription_id: dict | bytes
    :param body: subscription item to update.
    :type body: dict | bytes

    :rtype: Subscription
    """
    logging.info(f"update_subscription(): subscription_id={subscription_id}")
    subscriptionBody = None
    if connexion.request.is_json:
        subscriptionBody = Subscription.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_subscription(): subscriptionBody={subscriptionBody}")
    if subscriptionBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, 400

    subscription, status = search_subscription_by_id(subscription_id)
    if subscription is None or status == 404:
        problem = Problem(title="Not Found: program_id not found", status="404")
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, 404

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    subscription.modification_date_time = current_time

    if subscriptionBody.program_id != subscription.program_id:
        problem = Problem(title="Bad Request: program ID cannot be modified", status="400")
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, 400
    if subscriptionBody.client_name is not None:
        subscription.client_name = subscriptionBody.client_name
    if subscriptionBody.object_operations is not None:
        subscription.object_operations = subscriptionBody.object_operations
    if subscriptionBody.targets is not None:
        subscription.targets = subscriptionBody.targets

    subscription = objStore.update("SUBSCRIPTION", subscription)
    if type(subscription) is not Subscription:
        status = subscription
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, status

    logging.debug(f"update_subscription(): subscription={subscription}")

    subscription_callback("SUBSCRIPTION", "PUT", subscription)

    return (subscription)

def subscription_callback(resourceName, operation, object):
    logging.info(f"subscription_callback(): resourceName={resourceName}, operation={operation}")
    logging.debug(f"subscription_callback(): object={object}")

    subscriptions = objStore.search_all("SUBSCRIPTION")
    logging.debug(f"subscription_callback(): subscriptions={subscriptions}")
    if type(subscriptions) is not list:
        status = subscriptions
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"subscription_callback(): problem={problem}")
        return problem, status

    for subscription in subscriptions:
        resource = next((resource for resource in subscription.object_operations if
                         resourceName in resource.objects and operation in resource.operations), None)
        if resource is not None:
            if hasattr(object, "targets") and object.targets is not None and hasattr(subscription, "targets") and subscription.targets is not None:
                for target in object.targets:
                    targetObj = next((targetObj for targetObj in subscription.targets if
                                     targetObj.targetType in target.targetType), None)
                    if targetObj is not None:
                        if target.values is not None:
                            for value in target.values:
                                targetValue = next((targetValue for targetValue in targetObj.values if
                                       value in targetValue), None)

                            if targetValue is None:
                                logging.debug(f"subscription_callback: no matching targets")
                                return None
                    else:
                        logging.debug(f"subscription_callback: no matching targets")
                        return None

            notification = Notification(object_type=resourceName, operation=operation, targets=None, object=object)

            logging.info(f"subscription_callback(): notification={notification} callback_url={resource.callback_url}")
            headers = { "Authorization": f"Bearer {resource.bearer_token}"}

            response = requests.post(resource.callback_url, json=json.dumps(notification.to_dict()), headers=headers)
            if response.status_code != 200:
                logging.warning(f"subscription_callback: callback response.status_code={response.status_code}")
