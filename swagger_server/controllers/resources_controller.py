import connexion
from datetime import datetime
from http import HTTPStatus
import logging
from flask import request
from typing import Dict
from typing import Tuple
from typing import Union

from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.resource_name import ResourceName  # noqa: E501
from swagger_server.models.resource_request import ResourceRequest  # noqa: E501
from swagger_server.models.bl_resource_request import BlResourceRequest  # noqa: E501
from swagger_server.models.ven_resource_request import VenResourceRequest  # noqa: E501
from swagger_server.models.target import Target  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server.objStore.storageInterface import objStore
from swagger_server import util
from swagger_server import objectUtils

def create_resource(body):  # noqa: E501
    """create resource

    Create a new resource. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Resource
    """
    logging.info(f"create_resource(): ")
    targets = []
    if body["objectType"] in "VEN_RESOURCE_REQUEST":
        resourceBody = VenResourceRequest.from_dict(connexion.request.get_json())  # noqa: E501
        client_id = objectUtils.getClientId(request)
    else:
        resourceBody = BlResourceRequest.from_dict(connexion.request.get_json())
        client_id = resourceBody.client_id # noqa: E501
        if resourceBody.targets is not None:
            targets = resourceBody.targets

    # object must have unique name
    resources = objStore.search_all("RESOURCE")
    resourceList = [r for r in resources if r.resource_name == resourceBody.resource_name]
    if len(resourceList) > 0:
        return [], HTTPStatus.CONFLICT

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    resource = Resource(
        created_date_time=current_time,
        modification_date_time=None,
        object_type='RESOURCE',
        resource_name=resourceBody.resource_name,
        ven_id=resourceBody.ven_id,
        attributes=resourceBody.attributes,
        client_id=client_id,
        targets=targets
    )

    status = objStore.insert(resource)
    if status != HTTPStatus.CREATED:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_resource(): problem={problem}")
        return problem, status

    logging.debug(f"create_resource(): venResource={resource}")

    subscription_callback("RESOURCE", "CREATE", resource)
    return resource, HTTPStatus.CREATED


def delete_ven_resource(resource_id):  # noqa: E501
    """delete  ven resource

    Delete the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes

    :rtype: Resource
    """
    logging.info(f"delete_ven_resource(): resource_id={resource_id}")
    resource = objStore.remove("RESOURCE", resource_id)
    if type(resource) is not Resource:
        status = resource
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"delete_ven_resource(): problem={problem}")
        return problem, status

    subscription_callback("RESOURCE", "DELETE", resource)

    return resource, HTTPStatus.OK

def search_ven_resource_by_id(resource_id):  # noqa: E501
    """search ven resources by ID

    Return the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes

    :rtype: Resource
    """
    logging.info(f"search_ven_resource_by_id(): resource_id={resource_id}")
    resource = objStore.search("RESOURCE", resource_id)
    if type(resource) is not Resource:
        status = resource
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_resource_by_id(): problem={problem}")
        return problem, status

    # VEN can only read ven objects with client_id matching client_id associated with it's token
    if objectUtils.getClientRole(request) in 'VEN':
        client_id = objectUtils.getClientId(request)
        if resource.client_id != client_id:
            return [], HTTPStatus.OK

    subscription_callback("RESOURCE", "READ", resource)

    return resource, HTTPStatus.OK



def search_ven_resources(resource_name=None, ven_id=None, targets=None, skip=None, limit=None):  # noqa: E501
    """search ven resources

    List all ven resources associated with ven with specified venID. May filter results by resourceName as query params. May filter results by targets params. Use skip and pagination query params to limit response size.  # noqa: E501

    :param resource_name: Indicates resource objects with resourceName
    :type resource_name: dict | bytes
    :param ven_id: Indicates resource objects with venID
    :type ven_id: dict | bytes
    :param targets: Indicates targets
    :type targets: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Resource]
    """
    logging.info(
        f"search_ven_resources(): resource_name={resource_name} targets={targets} skip={skip} limit={limit}")
    # TBD: somehow string is received as '[/'name/']' ???
    if resource_name != None and resource_name[0] == '[':
        resource_name = resource_name[2: len(resource_name) - 2]

    resources = objStore.search_all("RESOURCE")
    logging.debug(f"search_ven_resourcess(): resources={resources}")
    if type(resources) is not list:
        status = resources
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_resourcess(): problem={problem}")
        return problem, status

    logging.info(f"search_ven_resourcess(): resources={resources}")

    objectList = resources
    # A VEN can only fetch a resource with a client_id matching the request token client_id
    if objectUtils.getClientRole(request) in 'VEN':
        client_id = objectUtils.getClientId(request)
        objectList = [r for r in objectList if r.client_id == client_id]

    logging.info(f"search_ven_resources(): objectList={objectList}")
    if resource_name != None:
        objectList = [r for r in objectList if r.resource_name == resource_name]
        if len(objectList) == 0:
            return [], HTTPStatus.OK
        else:
            return objectList, HTTPStatus.OK

    objectList = objectUtils.getObjectsWithTargets(objectList, targets)
    if skip != None:
        if len(objectList) < skip:
            return [], HTTPStatus.OK
        objectList = objectList[skip:]
    if limit != None:
        objectList = objectList[:limit]

    subscription_callback("RESOURCE", "READ", objectList)

    return objectList, HTTPStatus.OK


def update_ven_resource(resource_id, body=None):  # noqa: E501
    """update  ven resource

    Update the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes
    :param body: resource item to update.
    :type body: dict | bytes

    :rtype: Resource
    """
    logging.info(f"update_ven_resource(): resource_id={resource_id}")
    if body["objectType"] in "VEN_RESOURCE_REQUEST":
        resourceBody = VenResourceRequest.from_dict(connexion.request.get_json())  # noqa: E501
        if resourceBody is None:
            problem = Problem(title="Bad Request: No request body", status="400")
            logging.warning(f"update_resource(): problem={problem}")
            return problem, HTTPStatus.BAD_REQUEST
        client_id = objectUtils.getClientId(request)
        targets = []
    else:
        resourceBody = BlResourceRequest.from_dict(connexion.request.get_json())
        if resourceBody is None:
            problem = Problem(title="Bad Request: No request body", status="400")
            logging.warning(f"update_resource(): problem={problem}")
            return problem, HTTPStatus.BAD_REQUEST
        client_id = resourceBody.client_id  # noqa: E501
        if resourceBody.targets is not None:
            targets = resourceBody.targets
        else:
            targets = []

    resource, status = search_ven_resource_by_id(resource_id)
    if resource is None or status == HTTPStatus.NOT_FOUND:
        problem = Problem(title="Not Found: program_id not found", status="HTTPStatus.NOT_FOUND")
        logging.warning(f"update_resource(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND
    if client_id != resource.client_id and body["objectType"] in "VEN_RESOURCE_REQUEST":
        problem = Problem(title="Forbidden: client_id of request does not match object", status="403")
        logging.warning(f"update_resource(): problem={problem}")
        return problem, HTTPStatus.FORBIDDEN

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    resource.modification_date_time = current_time

    resource.ven_id = resourceBody.ven_id
    resource.resource_name = resourceBody.resource_name
    resource.attributes = resourceBody.attributes
    resource.targets = targets

    resource = objStore.update("RESOURCE", resource)
    if type(resource) is not Resource:
        status = resource
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_ven(): problem={problem}")
        return problem, status

    subscription_callback("RESOURCE", "UPDATE", resource)
    return resource, HTTPStatus.OK


