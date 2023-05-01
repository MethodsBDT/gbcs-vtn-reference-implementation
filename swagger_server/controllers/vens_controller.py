import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscriptions  # noqa: E501
from swagger_server import util


# recall this is just a toy VTN
maxResources = 3
maxVens = 3

vens = []
venID = 0

resources = [[] * maxResources] * maxVens
resourceIDs = [0] * maxResources

def create_resource(body, ven_id):  # noqa: E501
    """create resource

    Create a new resource. # noqa: E501

    :param body:
    :type body: dict | bytes
    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int

    :rtype: List[Resource]
    """
    logging.info(f"create_resource():")

    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_resource(): resourceBody={resourceBody}")
    if resourceBody is None:
        return []

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    global resourceIDs
    venResource = Resource(
        id=resourceIDs[ven_id],
        created_date_time=current_time,
        modification_date_time=None,
        resource_id=resourceBody.resource_id,
        target_values=resourceBody.target_values
    )

    resources[ven_id].insert(resourceIDs[ven_id], venResource)

    # bump resource ID
    resourceIDs[ven_id] += 1

    logging.debug(f"create_resource(): venResource={venResource}")

    for subscription in subscriptions:
        resource = next((resource for resource in subscription.resource_operations if
                         "RESOURCE" in resource.resources and "POST" in resource.operations), None)
        if resource is not None:
            logging.debug(f"create_resource(): resource={resource}")
            response = requests.post(resource.callback_url, json=json.dumps(venResource.to_dict()))
            if response.status_code != 200:
                logging.warning(f"create_resource: callback response.status_code={response.status_code}")

    return venResource


def create_ven(body):  # noqa: E501
    """create ven

    Create a new ven. # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: List[Ven]
    """
    logging.info(f"create_ven():")

    venBody = None
    if connexion.request.is_json:
        venBody = Ven.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_ven(): venBody={venBody}")
    if venBody is None:
        return []

    global venID
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    ven = Ven(
        id=venID,
        created_date_time=current_time,
        modification_date_time=None,
        ven_id=venBody.ven_id,
        target_values=venBody.target_values,
        resources=venBody.resources
    )

    # bump ven ID
    venID += 1

    vens.append(ven)
    logging.debug(f"create_ven(): ven={ven}")

    for subscription in subscriptions:
        resource = next((resource for resource in subscription.resource_operations if
                         "VEN" in resource.resources and "POST" in resource.operations), None)
        if resource is not None:
            logging.debug(f"create_ven(): resource={resource}")
            response = requests.post(resource.callback_url, json=json.dumps(ven.to_dict()))
            if response.status_code != 200:
                logging.warning(f"create_ven: callback response.status_code={response.status_code}")

    return ven


def delete_ven(ven_id):  # noqa: E501
    """delete  ven

    Delete the ven specified by venID specified in path. # noqa: E501

    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int

    :rtype: Ven
    """
    logging.info(f"delete_ven():")

    ven = next((ven for ven in vens if ven.id == ven_id), None)
    if ven is not None:
        vens.remove(ven)
        logging.debug(f"delete_ven(): ven={ven}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "VEN" in resource.resources and "DELETE" in resource.operations), None)
            if resource is not None:
                logging.debug(f"delete_ven(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(ven.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"delete_ven: callback response.status_code={response.status_code}")

        return ven
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_ven: problem={problem}")
        return problem

def delete_ven_resource(ven_id, resource_id):  # noqa: E501
    """delete  ven resource

    Delete the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int
    :param resource_id: Numeric ID of the associated resource.
    :type resource_id: int

    :rtype: Ven
    """
    logging.info(f"delete_resource():")

    venResource = next((venResource for venResource in resources[ven_id] if venResource.id == resource_id), None)

    if venResource is not None:
        resources[ven_id].remove(venResource)
        logging.debug(f"delete_ven_resource(): venResource={venResource}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "RESOURCE" in resource.resources and "DELETE" in resource.operations), None)
            if resource is not None:
                logging.debug(f"delete_ven_resource(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(venResource.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"delete_resource: callback response.status_code={response.status_code}")

        return venResource
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_ven_resource: problem={problem}")
        return problem

def search_ven_by_id(ven_id):  # noqa: E501
    """search vens by ID

    Return the ven specified by venID specified in path. # noqa: E501

    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int

    :rtype: Ven
    """
    logging.info(f"search_ven_by_id(): ven_id={ven_id}")
    ven = next((ven for ven in vens if ven.id == ven_id), None)
    logging.debug(f"search_ven_by_id(): ven={ven}")

    return ven


def search_ven_resource_by_id(ven_id, resource_id):  # noqa: E501
    """search ven resources by ID

    Return the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int
    :param resource_id: Numeric ID of the associated resource.
    :type resource_id: int

    :rtype: Resource
    """
    logging.info(f"search_ven_resource_by_id(): ven_id={ven_id} resource_id={resource_id}")
    resource = next((resource for resource in resources[ven_id] if resource.id == resource_id), None)
    logging.debug(f"search_ven_resource_by_id(): resource={resource}")

    return resource

def search_ven_resources(ven_id):  # noqa: E501
    """search ven resources

    Return the ven resources specified by venID specified in path. # noqa: E501

    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int

    :rtype: Resource
    """
    logging.info(f"search_ven_resources(): ven_id={ven_id}")

    return (resources[ven_id])

def search_vens(skip=None, limit=None):  # noqa: E501
    """search vens

    List all vens. Use skip and pagination query params to limit reponse size.  # noqa: E501

    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Ven]
    """
    logging.info(f"search_vens(): ")

    return (vens)



def update_ven(ven_id):  # noqa: E501
    """update  ven

    Update the ven specified by venID specified in path. # noqa: E501

    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int

    :rtype: Ven
    """
    logging.info(f"update_ven(): ven_id={ven_id}")

    venBody = None
    if connexion.request.is_json:
        venBody = Ven.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_ven(): venBody={venBody}")
    if venBody is None:
        return []

    ven = next((ven for ven in vens if ven.id == ven_id), None)
    if ven is not None:
        vens.remove(ven)

        # set modification date time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        ven.modification_date_time = current_time

        if venBody.ven_id is not None:
            ven.ven_id = venBody.ven_id
        if venBody.target_values is not None:
            ven.target_values = venBody.target_values
        if venBody.resources is not None:
            ven.resources = venBody.resources

        vens.append(ven)
        logging.debug(f"update_ven(): ven={ven}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "VEN" in resource.resources and "PUT" in resource.operations), None)
            if resource is not None:
                logging.debug(f"update_ven(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(ven.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"update_ven: callback response.status_code={response.status_code}")

        return (ven)

    return None

def update_ven_resource(ven_id, resource_id):  # noqa: E501
    """update  ven resource

    Update the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: Numeric ID of the associated ven.
    :type ven_id: int
    :param resource_id: Numeric ID of the associated resource.
    :type resource_id: int

    :rtype: Ven
    """
    logging.info(f"update_ven_resource(): ven_id={ven_id} resource_id={resource_id}")

    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_ven_resource(): resourceBody={resourceBody}")
    if resourceBody is None:
        return []

    venResource = next((venResource for venResource in resources[ven_id] if venResource.id == resource_id), None)
    if venResource is not None:
        resources[ven_id].remove(venResource)

        # set modification date time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        venResource.modification_date_time = current_time

        if resourceBody.resource_id is not None:
            venResource.resource_id = resourceBody.resource_id
        if resourceBody.target_values is not None:
            venResource.target_values = resourceBody.target_values

        resources[ven_id].insert(resourceIDs[ven_id], venResource)
        logging.debug(f"update_ven_resource(): venResource={venResource}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "RESOURCE" in resource.resources and "PUT" in resource.operations), None)
            if resource is not None:
                logging.debug(f"update_ven_resource(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(venResource.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"update_ven_resource: callback response.status_code={response.status_code}")

        return (venResource)

    return None
