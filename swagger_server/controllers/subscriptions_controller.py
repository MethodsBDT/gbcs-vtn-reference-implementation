import connexion
from datetime import datetime, timezone
from http import HTTPStatus
import logging
import requests
from flask import request
from typing import Dict
from typing import Tuple
from typing import Union

from swagger_server.models.object_types import ObjectTypes  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.subscription import Subscription  # noqa: E501
from swagger_server.models.subscription_request import SubscriptionRequest  # noqa: E501
from swagger_server.models.notification import Notification  # noqa: E501
from swagger_server.objStore.storageInterface import objStore
from swagger_server.models.target import Target  # noqa: E501
from swagger_server import util
from swagger_server import objectUtils
from swagger_server import notifiers


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
        subscriptionBody = SubscriptionRequest.from_dict(connexion.request.get_json())  # noqa: E501

    # object may refer to an existing program
    programs = objStore.search_all("PROGRAM")
    programList = [p for p in programs if p.id == subscriptionBody.program_id]
    if len(programList) == 1:
        # TBD : add logic to limit callbacks to objects asscociated with this program
        pass

    # Note: there is currently no concept of a duplicated subscription
    client_id = objectUtils.getClientId(request)

    now = datetime.now(timezone.utc)
    current_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    subscription = Subscription(
        created_date_time=current_time,
        modification_date_time=current_time,
        object_type='SUBSCRIPTION',
        client_id=client_id,
        client_name=subscriptionBody.client_name,
        program_id=subscriptionBody.program_id,
        object_operations=subscriptionBody.object_operations,
        targets = subscriptionBody.targets
    )

    status = objStore.insert(subscription)
    if status != HTTPStatus.CREATED:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_subscription(): problem={problem}")
        return problem, status

    status = subscription_callback_echo_test(subscriptionBody.object_operations)
    if status != HTTPStatus.OK:
        problem = Problem(title="Echo issue", status=str(status))
        logging.warning(f"create_subscription(): problem={problem}")
        return problem, status

    subscription_callback("SUBSCRIPTION", "CREATE", subscription)

    return subscription, HTTPStatus.CREATED


def delete_subscription(subscription_id):  # noqa: E501
    """delete  subscription

    Delete the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: object ID of the associated subscription.
    :type subscription_id: str

    :rtype: Union[Subscription, Tuple[Subscription, int], Tuple[Subscription, int, Dict[str, str]]
    """
    logging.info(f"delete_subscription(): subscription_id={subscription_id}")

    subscription = objStore.remove("SUBSCRIPTION", subscription_id)
    if type(subscription) is not Subscription:
        status = subscription
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"delete_subscription(): problem={problem}")
        return problem, status

    subscription_callback("SUBSCRIPTION", "DELETE", subscription)

    return subscription, HTTPStatus.OK

def search_subscription_by_id(subscription_id):  # noqa: E501
    """search subscriptions by ID

    Return the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: object ID of the associated subscription.
    :type subscription_id: str

    :rtype: Union[Subscription, Tuple[Subscription, int], Tuple[Subscription, int, Dict[str, str]]
    """
    logging.info(f"search_subscription_by_id(): subscription_id={subscription_id}")

    subscription = objStore.search("SUBSCRIPTION", subscription_id)
    logging.debug(f"search_all_subscriptions(): subscription={subscription}")
    if type(subscription) is not Subscription:
        status = subscription
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_subscriptions(): problem={problem}")
        return problem, status

    # VEN may only view subscriptions its created
    if objectUtils.getClientRole(request) in 'VEN':
        client_id = objectUtils.getClientId(request)
        if subscription.client_id != client_id:
            return None, HTTPStatus.NOT_FOUND

    subscription_callback("SUBSCRIPTION", "READ", subscription)

    return subscription, HTTPStatus.OK

def search_subscriptions(program_id=None, client_name=None, objects=None, skip=None, limit=None):  # noqa: E501
    """search subscriptions

    List all subscriptions. May filter results by programID and clientName as query params. May filter results by objects as query param. See objectTypes schema. Use skip and pagination query params to limit response size.  # noqa: E501

    :param program_id: filter results to subscriptions with programID.
    :type program_id: dict | bytes
    :param client_name: filter results to subscriptions with clientName.
    :type client_name: dict | bytes
    :param objects: list of objects to subscribe to.
    :type objects: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Subscription]
    """
    # TBD: see genereated server, need ot add fetching params from request?
    logging.info(
        f"search_all_subscriptions(): program_id={program_id} client_name={client_name} objects={objects} skip={skip} limit={limit}")

    subscriptions = objStore.search_all("SUBSCRIPTION")
    logging.debug(f"search_all_subscriptions(): subscriptions={subscriptions}")
    if type(subscriptions) is not list:
        status = subscriptions
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_subscriptions(): problem={problem}")
        return problem, status

    # if request from VEN filter on reports created by this VEN
    if objectUtils.getClientRole(request) in 'VEN':
        client_id = objectUtils.getClientId(request)
        subscriptions = [subscription for subscription in subscriptions if subscription.client_id == client_id]

    if program_id != None:
        subscriptions = [subscription for subscription in subscriptions if subscription.program_id == program_id]
        if len(subscriptions) == 0:
            return subscriptions, HTTPStatus.OK
    if client_name != None:
        subscriptions = [subscription for subscription in subscriptions if subscription.client_name == client_name]
        if len(subscriptions) == 0:
            return subscriptions, HTTPStatus.OK
    # TBD: sesrch by objects
    if skip != None:
        if len(subscriptions) < skip:
            return [], HTTPStatus.OK
        subscriptions = subscriptions[skip:]
    if limit != None:
        subscriptions = subscriptions[:limit]

    logging.debug(f"search_all_subscriptions(): subscriptions={subscriptions}")

    subscription_callback("SUBSCRIPTION", "READ", subscriptions)
    return subscriptions


def update_subscription(subscription_id, body=None):  # noqa: E501
    """update  subscription

    Update the subscription specified by subscriptionID specified in path. # noqa: E501

    :param subscription_id: object ID of the associated subscription.
    :type subscription_id: str
    :param subscription_request: subscription item to update.
    :type subscription_request: dict | bytes

    :rtype: Union[Subscription, Tuple[Subscription, int], Tuple[Subscription, int, Dict[str, str]]
    """
    logging.info(f"update_subscription(): subscription_id={subscription_id}")
    subscriptionBody = None
    if connexion.request.is_json:
        subscriptionBody = SubscriptionRequest.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_subscription(): subscriptionBody={subscriptionBody}")
    if subscriptionBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, HTTPStatus.BAD_REQUEST

    subscription, status = search_subscription_by_id(subscription_id)
    if subscription is None or status == HTTPStatus.NOT_FOUND:
        problem = Problem(title="Not Found: subscription not found", status="404")
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND
    client_id = objectUtils.getClientId(request)
    if client_id != subscription.client_id:
        problem = Problem(title="Forbidden: client_id of request does not match object", status="403")
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, HTTPStatus.FORBIDDEN

    # set modification date time
    now = datetime.now(timezone.utc)
    current_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    subscription.modification_date_time = current_time

    subscription.program_id = subscriptionBody.program_id
    subscription.client_name = subscriptionBody.client_name
    subscription.object_operations = subscriptionBody.object_operations
    subscription.targets = subscriptionBody.targets

    subscription = objStore.update("SUBSCRIPTION", subscription)
    if type(subscription) is not Subscription:
        status = subscription
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_subscription(): problem={problem}")
        return problem, status

    logging.debug(f"update_subscription(): subscription={subscription}")

    subscription_callback("SUBSCRIPTION", "UPDATE", subscription)

    return (subscription)

def subscription_callback(resourceName, operation, object):
    logging.info(f"subscription_callback(): resourceName={resourceName}, operation={operation}")
    logging.debug(f"subscription_callback(): object={object}")

    # Dispatch notifiers for non-WEBHOOK bindings
    notifiers.dispatch(resourceName, operation, object)

    subscriptions = objStore.search_all("SUBSCRIPTION")
    logging.debug(f"subscription_callback(): subscriptions={subscriptions}")
    if type(subscriptions) is not list:
        status = subscriptions
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"subscription_callback(): problem={problem}")
        return problem, status

    for subscription in subscriptions:
        objOperation = next((objOperation for objOperation in subscription.object_operations if
                         resourceName in objOperation.objects and operation in objOperation.operations), None)
        if objOperation is not None:
            match = True
            if hasattr(object, "targets") and object.targets is not None and subscription.targets is not None:
                # If subscription is created by VEN, get associated ven.targets to determine 'allowed' targets
                # TDB: we currently do not have a way to determine if subscription is associated with a BL or VEN client
                allowed_targets = objectUtils.getAllowedTargets(subscription.client_id)
                # get intersection of allowed targets and targets in subscription
                targets = [t for t in allowed_targets if t in subscription.targets]

                match = False
                for t in targets:
                    # if any target string in subscription matches any target in object, there is a match
                    if t in object.targets:
                        match = True
                        break

            if match is True:
                notification = Notification(object_type=resourceName, operation=operation, targets=None, object=object)

                logging.info(f"subscription_callback(): notification={notification} callback_url={objOperation.callback_url}")
                headers = { "Authorization": f"Bearer {objOperation.bearer_token}"}

                # FS TBD: address timeout error
                response = requests.post(objOperation.callback_url, json=notification.to_json_dict(), headers=headers)
                if response.status_code != HTTPStatus.OK:
                    logging.warning(f"subscription_callback: callback response.status_code={response.status_code}")

def subscription_callback_echo_test(operations):
    logging.info(f"subscription_callback_echo_test(): operations={operations}")

    # verify callback service by sending request with echo parameter
    for operation in operations:
        logging.info(f"subscription_callback_echo_test(): operation={operation}")

        # TBD: clean up this section
        headers = {"Authorization": f"Bearer {operation.bearer_token}"}
        params = {"echo": "test_echo"}

        try:
            response = requests.get(operation.callback_url+"/echo", params=params, headers=headers)

            if response.status_code != HTTPStatus.OK:
                logging.warning(f"subscription_callback: callback response.status_code={response.status_code}")
            content = response.content.decode('utf8').replace("'", '"')
            if "test_echo" not in content:
                logging.warning(f"subscription_callback: callback content={content}")
                return HTTPStatus.INTERNAL_SERVER_ERROR
            return HTTPStatus.OK
        except Exception as e:
            # For testing purposes
            logging.error(f"subscription_callback_echo_test(): exception={e}")
            return HTTPStatus.OK
