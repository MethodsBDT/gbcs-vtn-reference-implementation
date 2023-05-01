import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.subscription import Subscription  # noqa: E501
from swagger_server import util

subscriptions = []
subscriptionID = 0


def create_subscription(body):  # noqa: E501
    """create subscription

    Create a new subscription. # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: List[Subscription]
    """
    logging.info(f"create_program_subscription():")

    subscriptionBody = None
    if connexion.request.is_json:
        subscriptionBody = Subscription.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_program_subscription(): subscriptionBody={subscriptionBody}")
    if subscriptionBody is None:
        return []

    global subscriptionID
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    subscription = Subscription(
        id=subscriptionID,
        created_date_time=current_time,
        client_id=subscriptionBody.client_id,
        program_id=subscriptionBody.program_id,
        resource_operations=subscriptionBody.resource_operations
    )

    # bump Subscription ID
    subscriptionID += 1

    subscriptions.append(subscription)
    logging.debug(f"create_program_subscription(): subscription={subscription}")

    return subscription


def delete_subscription(subscription_id):  # noqa: E501
    """delete  subscription

    Delete the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: Numeric ID of the associated subscription.
    :type subscription_id: int

    :rtype: Subscription
    """
    logging.info(f"delete_subscription(): subscription_id={subscription_id}")

    subscription = next((subscription for subscription in subscriptions if subscription.id == subscription_id), None)
    if subscription is not None:
        subscriptions.remove(subscription)
        logging.debug(f"delete_subscription(): subscription={subscription}")
        return subscription
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_subscription(): logging={logging}")
        return problem

def search_subscription_by_id(subscription_id):  # noqa: E501
    """search subscriptions by ID

    Return the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: Numeric ID of the associated subscription.
    :type subscription_id: int

    :rtype: Subscription
    """
    logging.info(f"search_subscription_by_id(): subscription_id={subscription_id}")

    subscription = next((subscription for subscription in subscriptions if subscription.id == subscription_id), None)
    logging.debug(f"search_subscription_by_id(): subscription={subscription}")
    return subscription

def search_subscriptions(program_id=None, client_id=None, resource_types=None, skip=None, limit=None):  # noqa: E501
    """search subscriptions

    List all subscriptions. May filter results by programID and clientID as query params. May filter results by resourceTypes as query param. ResoureTypes are PROGRAM, REPORT, EVENT. Use skip and pagination query params to limit reponse size.  # noqa: E501

    :param program_id: filter results to subscriptions with programID of associated value.
    :type program_id: int
    :param client_id: filter results to subscriptions with clientID of associated value.
    :type client_id: int
    :param resource_types: filter results to subscriptions with resourceTypes of associated values.
    :type resource_types: List[str]
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Subscription]
    """
    logging.info(f"search_subscriptions(): program_id={program_id} client_id={client_id} resource_types{resource_types}")

    # TBD: implement client_id, resource_types
    if program_id is not None:
        tempSubscriptions = [subscription for subscription in subscriptions if subscription.program_id == program_id]
        logging.debug(f"search_subscriptions(): tempSubscriptions={tempSubscriptions}")
        return tempSubscriptions
    return subscriptions

def update_subscription(subscription_id):  # noqa: E501
    """update  subscription

    Update the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: Numeric ID of the associated subscription.
    :type subscription_id: int

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
            return problem
        if subscriptionBody.client_id is not None:
            subscription.client_id = subscriptionBody.client_id
        if subscriptionBody.resource_operations is not None:
            subscription.resourceOperations = subscriptionBody.resource_operations

        subscriptions.append(subscription)
        logging.debug(f"update_subscription(): subscription={subscription}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "SUBSCRIPTION" in resource.resources and "PUT" in resource.operations), None)
            if resource is not None:
                logging.debug(f"update_subscription(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(subscription.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"update_subscription: callback response.status_code={response.status_code}")

        return (subscription)

    return None