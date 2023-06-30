import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.notification import Notification  # noqa: E501
from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.object_types import ObjectTypes  # noqa: E501
from swagger_server.models.subscription import Subscription  # noqa: E501
from swagger_server.models.target import Target  # noqa: E501
from swagger_server import util

subscriptions = []
subscriptionID = 0


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
        logging.debug(f"create_subscription(): subscriptionBody={subscriptionBody}")
    if subscriptionBody is None:
        return []

    global subscriptionID
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    subscription = Subscription(
        id=str(subscriptionID),
        created_date_time=current_time,
        client_name=subscriptionBody.client_name,
        program_id=subscriptionBody.program_id,
        object_operations=subscriptionBody.object_operations,
        targets = subscriptionBody.targets
    )

    # bump Subscription ID
    subscriptionID += 1

    subscriptions.append(subscription)
    logging.debug(f"create_subscription(): subscription={subscription}")
    logging.info(f"create_subscription(): subscription={subscription}")

    subscription_callback("SUBSCRIPTION", "POST", subscription)

    return subscription


def delete_subscription(subscription_id):  # noqa: E501
    """delete  subscription

    Delete the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: object ID of the associated subscription.
    :type subscription_id: dict | bytes

    :rtype: Subscription
    """
    logging.info(f"delete_subscription(): subscription_id={subscription_id}")

    subscription = next((subscription for subscription in subscriptions if subscription.id == subscription_id), None)
    if subscription is not None:
        subscriptions.remove(subscription)
        logging.debug(f"delete_subscription(): subscription={subscription}")

        subscription_callback("SUBSCRIPTION", "DELETE", subscription)

        return subscription
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_subscription(): logging={logging}")
        return problem, 404

def search_subscription_by_id(subscription_id):  # noqa: E501
    """search subscriptions by ID

    List all subscriptions. May filter results by programID and clientID as query params. May filter results by objects as query param. See objectTypes schema. Use skip and pagination query params to limit response size.  # noqa: E501

    :param program_id: filter results to subscriptions with programID.
    :type program_id: dict | bytes
    :param client_name: filter results to subscriptions with clientName.
    :type client_name: str
    :param targets: return programs that match requested targets
    :type targets: list | bytes
    :param objects: list of objects to subscribe to.
    :type objects: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Subscription]
    """
    logging.info(f"search_subscription_by_id(): subscription_id={subscription_id}")

    if connexion.request.is_json:
        program_id = ObjectID.from_dict(connexion.request.get_json())  # noqa: E501
    if connexion.request.is_json:
        targets = [Target.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    if connexion.request.is_json:
        objects = [ObjectTypes.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501

    subscription = next((subscription for subscription in subscriptions if subscription.id == subscription_id), None)
    logging.debug(f"search_subscription_by_id(): subscription={subscription}")
    return subscription

def search_subscriptions(program_id=None, client_name=None, targets=None, objects=None, skip=None, limit=None):  # noqa: E501
    """search subscriptions

    List all subscriptions. May filter results by programID and clientID as query params. May filter results by objects as query param. See objectTypes schema. Use skip and pagination query params to limit response size.  # noqa: E501
    
    :param program_id: filter results to subscriptions with programID.
    :type program_id: dict | bytes
    :param client_name: filter results to subscriptions with clientIdentifier.
    :type client_name: str
    :param targets: return programs that match requested targets
    :type targets: list | bytes
    :param objects: list of objects to subscribe to.
    :type objects: list | bytes
     :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Subscription]
    """
    logging.info(f"search_subscriptions(): program_id={program_id} client_name={client_name} objects{objects}")

    # TBD: implement client_id, objects
    if program_id is not None:
        tempSubscriptions = [subscription for subscription in subscriptions if subscription.program_id == program_id]
        logging.debug(f"search_subscriptions(): tempSubscriptions={tempSubscriptions}")
        return tempSubscriptions
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
        return []

    subscription = next((subscription for subscription in subscriptions if subscription.id == subscription_id), None)
    if subscription is not None:
        subscriptions.remove(subscription)

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

        subscriptions.append(subscription)
        logging.debug(f"update_subscription(): subscription={subscription}")

        subscription_callback("SUBSCRIPTION", "PUT", subscription)

        return (subscription)

    return None


def subscription_callback(resourceName, operation, object):
    logging.info(f"subscription_callback(): resourceName={resourceName}, operation={operation}, object={object}")
    # print(f"subscription_callback(): subscriptions={subscriptions}")

    for subscription in subscriptions:
        # print(f"subscription_callback(): subscription={subscription}")
        resource = next((resource for resource in subscription.object_operations if
                         resourceName in resource.objects and operation in resource.operations), None)
        if resource is not None:
            # print(f"    subscription_callback(): resource={resource}")
            if object.targets is not None and subscription.targets is not None:
                for target in object.targets:
                    # print(f"        subscription_callback(): target={target}")
                    targetObj = next((targetObj for targetObj in subscription.targets if
                                     targetObj.targetType in target.targetType), None)
                    if targetObj is not None:
                        # print(f"            subscription_callback(): targetObj={targetObj}")
                        if target.values is not None:
                            for value in target.values:
                                # print(f"subscription_callback(): value={value}")
                                targetValue = next((targetValue for targetValue in targetObj.values if
                                       value in targetValue), None)

                            # print(f"                subscription_callback(): targetValue={targetValue}")
                            if targetValue is None:
                                logging.debug(f"subscription_callback: no matching targets")
                                return None
                    else:
                        logging.debug(f"subscription_callback: no matching targets")
                        return None


            notification = Notification(object_type=resourceName, operation=operation, targets=None, object=object)

            logging.debug(f"subscription_callback(): notification={notification}")
            logging.info(f"subscription_callback(): notification={notification}")

            response = requests.post(resource.callback_url, json=json.dumps(notification.to_dict()))
            if response.status_code != 200:
                logging.warning(f"subscription_callback: callback response.status_code={response.status_code}")
