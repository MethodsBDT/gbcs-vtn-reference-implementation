import connexion
from datetime import datetime
from http import HTTPStatus
import logging
from flask import request
from typing import Dict
from typing import Tuple
from typing import Union

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.resource_request import ResourceRequest  # noqa: E501
from swagger_server.models.bl_resource_request import BlResourceRequest  # noqa: E501
from swagger_server.models.ven_resource_request import VenResourceRequest  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.models.ven_request import VenRequest  # noqa: E501
from swagger_server.models.bl_ven_request import BlVenRequest  # noqa: E501
from swagger_server.models.ven_ven_request import VenVenRequest  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server.objStore.storageInterface import objStore
from swagger_server import util

# recall this is just a toy VTN
MAX_RESOURCES = 3
# always incrementing
resource_id = 0

def create_ven(body):  # noqa: E501
    """create ven

    Create a new ven. # noqa: E501

    :param ven_request:
    :type ven_request: dict | bytes

    :rtype: Union[Ven, Tuple[Ven, int], Tuple[Ven, int, Dict[str, str]]
    """
    logging.info(f"create_ven(): ")

    targets = []
    if body["objectType"] in "VEN_VEN_REQUEST":
        venBody = VenVenRequest.from_dict(connexion.request.get_json())  # noqa: E501
        client_id = util.getClientId(request)
    else:
        venBody = BlVenRequest.from_dict(connexion.request.get_json())
        client_id = venBody.client_id # noqa: E501
        if venBody.targets is not None:
            targets = venBody.targets

    # object must have unique client_id
    vens = objStore.search_all("VEN")
    vensList = [v for v in vens if v.client_id == client_id]
    if len(vensList) > 0:
        return [], HTTPStatus.CONFLICT

    # object must have unique name
    vens = objStore.search_all("VEN")
    vensList = [v for v in vens if v.ven_name == venBody.ven_name]
    if len(vensList) > 0:
        return [], HTTPStatus.CONFLICT

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    ven = Ven(
        created_date_time=current_time,
        modification_date_time=None,
        object_type='VEN',
        ven_name=venBody.ven_name,
        attributes=venBody.attributes,
        client_id=client_id,
        targets=targets
    )

    # FS TBD: why doesn't this pattern apply to attributes?
    if venBody.resources is not None:
        ven.resources = venBody.resources
    else:
        ven.resources = []

    status = objStore.insert(ven)
    if status != HTTPStatus.CREATED:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_ven(): problem={problem}")
        return problem, status

    subscription_callback("VEN", "CREATE", ven)
    return ven, HTTPStatus.CREATED

def delete_ven(ven_id):  # noqa: E501
    """delete  ven

    Delete the ven specified by venID specified in path. # noqa: E501

    :param ven_id: object ID of ven.
    :type ven_id: str

    :rtype: Union[Ven, Tuple[Ven, int], Tuple[Ven, int, Dict[str, str]]
    """

    logging.info(f"delete_ven(): ven_id={ven_id}")
    ven = objStore.remove("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"delete_ven(): problem={problem}")
        return problem, status

    subscription_callback("VEN", "DELETE", ven)

    return ven, HTTPStatus.OK


def search_ven_by_id(ven_id):  # noqa: E501
    """search vens by ID

    Return the ven specified by venID specified in path. # noqa: E501

    :param ven_id: object ID of ven.
    :type ven_id: dict | bytes

    :rtype: Ven
    """
    logging.info(f"search_ven_by_id(): ven_id={ven_id}")
    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_by_id(): problem={problem}")
        return problem, status

    # VEN can only read ven objects with client_id matching client_id associated with it's token
    if util.getClientRole(request) in 'VEN':
        client_id = util.getClientId(request)
        if ven.client_id != client_id:
            return [], HTTPStatus.OK

    subscription_callback("VEN", "READ", ven)

    return ven, HTTPStatus.OK

def search_vens(ven_name=None, target_type=None, target_values=None, skip=None, limit=None):  # noqa: E501
    """search vens

    List all vens. May filter results by venName as query param. May filter results by targetType and targetValues as query params. Use skip and pagination query params to limit response size.  # noqa: E501

    :param ven_name: Indicates ven objects w venName
    :type ven_name: dict | bytes
    :param target_type: Indicates targeting type, e.g. GROUP
    :type target_type: dict | bytes
    :param target_values: List of target values, e.g. group names
    :type target_values: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Ven]
    """
    logging.info(
        f"search_vens(): ven_name={ven_name} target_type={target_type} target_values={target_values} skip={skip} limit={limit}")

    vens = objStore.search_all("VEN")
    logging.debug(f"search_vens(): vens={vens}")
    if type(vens) is not list:
        status = vens
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_vens(): problem={problem}")
        return problem, status

    logging.info(f"search_vens(): vens={vens}")
    venList = vens

    # A VEN can only fetch a ven with a client_id matching the request token client_id
    # FS TBD: allow VEN to specify targets? (why?)
    if util.getClientRole(request) in 'VEN':
        client_id = util.getClientId(request)
        # There can ony be one ven with a given client_id
        venList = [ven for ven in vens if ven.client_id == client_id]
        if len(venList) > 1:
            logging.warning(f"search_vens(): multiple vens with same client_id={client_id}")
        return venList, HTTPStatus.OK

    if ven_name != None:
        venList = [ven for ven in vens if ven.ven_name == ven_name]
        if len(venList) == 0:
            return [], HTTPStatus.OK
    
    venList = util.getObjectsWithTarget(venList, target_type, target_values)
    if skip != None:
        if len(vens) < skip:
            return [], HTTPStatus.OK
        venList = vens[skip:]
    if limit != None:
        venList = venList[:limit]

    logging.debug(f"search_vens(): venList={venList}")

    subscription_callback("VEN", "READ", venList)

    return venList, HTTPStatus.OK

def update_ven(ven_id, body=None):  # noqa: E501
    """update  ven

    Update the ven specified by venID specified in path. # noqa: E501

    :param ven_id: object ID of ven.
    :type ven_id: dict | bytes
    :param body: ven item to update.
    :type body: dict | bytes

    :rtype: Ven
    """
    logging.info(f"update_ven(): ven_id={ven_id}")

    venBody = None
    if body["objectType"] in "VEN_VEN_REQUEST":
        venBody = VenVenRequest.from_dict(connexion.request.get_json())  # noqa: E501
        client_id = util.getClientId(request)
        targets = []
    else:
        venBody = BlVenRequest.from_dict(connexion.request.get_json())
        client_id = venBody.client_id  # noqa: E501
        if venBody.targets is not None:
            targets = venBody.targets
        else:
            targets = []

    if venBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_ven(): problem={problem}")
        return problem, HTTPStatus.BAD_REQUEST

    ven, status = search_ven_by_id(ven_id)
    if ven is None or status == HTTPStatus.NOT_FOUND:
        problem = Problem(title="Not Found: program_id not found", status="404")
        logging.warning(f"update_ven(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    ven.modification_date_time = current_time

    if venBody.ven_name is not None:
        ven.ven_name = venBody.ven_name
    if venBody.resources is not None:
        ven.resources = venBody.resources
    if venBody.attributes is not None:
        ven.attributes = venBody.attributes,
    ven.target = targets
    ven.client_id = client_id

    ven = objStore.update("VEN", ven)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_ven(): problem={problem}")
        return problem, status

    subscription_callback("VEN", "UPDATE", ven)
    return ven

def create_resource(body, ven_id):  # noqa: E501
    """create resource

    Create a new resource. # noqa: E501

    :param body:
    :type body: dict | bytes
    :param ven_id: Numeric ID of ven.
    :type ven_id: dict | bytes

    :rtype: Resource
     """
    logging.info(f"create_resource(): ven_id={ven_id}")
    global resource_id

    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_resource(): problem={problem}")
        return problem, status

    targets = []
    if body["objectType"] in "VEN_RESOURCE_REQUEST":
        resourceBody = VenResourceRequest.from_dict(connexion.request.get_json())  # noqa: E501
    else:
        resourceBody = BlResourceRequest.from_dict(connexion.request.get_json())
        if resourceBody.targets is not None:
            targets = resourceBody.targets

    logging.debug(f"search_all_ven_resources(): ven.resources={ven.resources}")

    # object must have unique name
    resources = ven.resources
    resourceList = [r for r in resources if r.resource_name == resourceBody.resource_name]
    if len(resourceList) > 0:
        return [], HTTPStatus.CONFLICT

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    venResource = Resource(
        id=str(resource_id),
        created_date_time=current_time,
        modification_date_time=None,
        object_type='RESOURCE',
        resource_name=resourceBody.resource_name,
        ven_id = ven_id,
        attributes=resourceBody.attributes,
        targets=targets
    )

    resource_id += 1

    ven.resources.append(venResource)
    ven = objStore.update("VEN", ven)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_ven(): problem={problem}")
        return problem, status

    logging.debug(f"create_resource(): venResource={venResource}")

    subscription_callback("RESOURCE", "CREATE", venResource)
    return venResource, HTTPStatus.CREATED

def delete_ven_resource(ven_id, resource_id):  # noqa: E501
    """delete  ven resource

    Delete the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: object ID of the associated ven.
    :type ven_id: dict | bytes
    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes

    :rtype: Resource
    """
    logging.info(f"delete_ven_resource(): ven_id={ven_id} resource_id={resource_id}")

    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_by_id(): problem={problem}")
        return problem, status

    logging.debug(f"delete_ven_resource(): ven={ven}")

    if len(ven.resources) == 0:
        problem = Problem(title="Not Found: no resources in system", status="404")
        logging.warning(f"delete_ven_resource(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    venResource = next((venResource for venResource in ven.resources if venResource.id == resource_id), None)
    if venResource is None:
        problem = Problem(title="Not Found: resource_id not found", status="404")
        logging.warning(f"delete_ven_resource: problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    logging.debug(f"delete_ven_resource(): venResource={venResource}")
    logging.debug(f"delete_ven_resource(): ven.resources={ven.resources}")

    ven.resources.remove(venResource)
    subscription_callback("RESOURCE", "DELETE", venResource)
    return venResource

def search_ven_resources(ven_id, resource_name=None, target_type=None, target_values=None, skip=None, limit=None):  # noqa: E501
    """search ven resources

    Return the ven resources specified by venID specified in path. # noqa: E501
   :param ven_id: Numeric ID of ven.
    :type ven_id: dict | bytes
    :param resource_name: Indicates resource objects with resourceName
    :type resource_name: dict | bytes
    :param target_type: Indicates targeting type, e.g. GROUP
    :type target_type: dict | bytes
    :param target_values: List of target values, e.g. group names
    :type target_values: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int


    :rtype: Resource
    """
    logging.info(
        f"search_ven_resources(): resource_name={resource_name} target_type={target_type} target_values={target_values} skip={skip} limit={limit}")
    # TBD: somehow string is received as '[/'name/']' ???
    if resource_name != None and resource_name[0] == '[':
        resource_name = resource_name[2: len(resource_name) - 2]

    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_resources(): problem={problem}")
        return problem, status

    # A VEN can only fetch a ven with a client_id matching the request token client_id
    if util.getClientRole(request) in 'VEN':
        client_id = util.getClientId(request)
        if ven.client_id != client_id:
            logging.warning(f"search_ven_resources(): client_id of ven={ven.client_id} does not match requestor's client_id={client_id}")
            # FS TBD: should return NOT_FOUND?
            return [], HTTPStatus.OK

    resourceList = ven.resources
    logging.info(f"search_ven_resources(): resourceList={resourceList}")
    if resource_name != None:
        # for resource in resourceList:
        #     logging.info(f"resource.resource_name={resource.resource_name} resource_name={resource_name}")

        resourceList = [resource for resource in ven.resources if resource.resource_name == resource_name]
        # logging.info(f"search_ven_resources(): resourceList={resourceList}")
        if len(resourceList) == 0:
            return resourceList, HTTPStatus.OK
    logging.info(f"search_ven_resources(): resourceList={resourceList}")
    resourceList = util.getTargets(resourceList, target_type, target_values)
    if skip != None:
        if len(resourceList) < skip:
            return [], HTTPStatus.OK
        resourceList = resourceList[skip:]
    if limit != None:
        resourceList = resourceList[:limit]
    logging.debug(f"search_ven_resources(): resourceList={resourceList}")

    subscription_callback("RESOURCE", "READ", resourceList)

    return resourceList

def search_ven_resource_by_id(ven_id, resource_id):  # noqa: E501
    """search ven resources by ID

    Return the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: object ID of the associated ven.
    :type ven_id: dict | bytes
    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes

    :rtype: Resource
    """
    # find index in vens of ven_id
    logging.info(f"search_ven_resource_by_id(): ven_id={ven_id} resource_id={resource_id}")

    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_by_id(): problem={problem}")
        return problem, status

    # A VEN can only fetch a ven with a client_id matching the request token client_id
    if util.getClientRole(request) in 'VEN':
        client_id = util.getClientId(request)
        if ven.client_id != client_id:
            logging.warning(f"search_ven_resources(): client_id of ven={ven.client_id} does not match requestor's client_id={client_id}")
            # FS TBD: should return NOT_FOUND?
            return [], HTTPStatus.OK

    logging.debug(f"search_ven_resource_by_id(): ven={ven}")

    if len(ven.resources) == 0:
        problem = Problem(title="Not Found: no resources in system", status="404")
        logging.warning(f"search_ven_resource_by_id(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    resource = next((resource for resource in ven.resources if resource.id == resource_id), None)
    if resource is None:
        problem = Problem(title="Not Found: resource_id not found", status="404")
        logging.warning(f"search_ven_resource_by_id(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    logging.debug(f"search_ven_resource_by_id(): resource={resource}")

    subscription_callback("RESOURCE", "READ", resource)

    return resource

def update_ven_resource(ven_id, resource_id, body=None):  # noqa: E501
    """update  ven resource

    Update the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: object ID of the associated ven.
    :type ven_id: dict | bytes
    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes
    :param body: resource item to update.
    :type body: dict | bytes

    :rtype: Resource
    """
    logging.info(f"update_ven_resource(): ven_id={ven_id} resource_id={resource_id}")
    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, status

    logging.debug(f"update_ven_resource(): ven={ven}")

    if len(ven.resources) == 0:
        problem = Problem(title="Not Found: no resources in system", status="404")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    if body is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, HTTPStatus.BAD_REQUEST

    targets = []
    if body["objectType"] in "VEN_RESOURCE_REQUEST":
        resourceBody = VenResourceRequest.from_dict(connexion.request.get_json())  # noqa: E501
    else:
        resourceBody = BlResourceRequest.from_dict(connexion.request.get_json())
        if resourceBody.targets is not None:
            targets = venBody.targets

    if resourceBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, HTTPStatus.BAD_REQUEST

    venResource = next((venResource for venResource in ven.resources if venResource.id == resource_id), None)
    if venResource is None:
        problem = Problem(title="Not Found: resource_id not found", status="404")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    ven.resources.remove(venResource)

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    venResource.modification_date_time = current_time

    if resourceBody.resource_name is not None:
        venResource.resource_name = resourceBody.resource_name
    venResource.targets = targets
    if resourceBody.attributes is not None:
        venResource.attributes = resourceBody.attributes,

    logging.debug(f"update_ven_resource(): venResource={venResource}")
    ven.resources.append(venResource)
    subscription_callback("RESOURCE", "UPDATE", venResource)
    return (venResource)

def getUnionOfTargets(request, target_type, target_values):
    # get targets of ven object with client_id associated with requestor's token
    client_id = util.getClientId(request)
    vens = objStore.search_all("VEN")
    venList = [ven for ven in vens if ven.client_id == client_id]
    if 0 == len(venList) < 2:
        logging.warning(f"vens_controller.allowedTargets(): none or multiple vens with client_id {client_id} venList={venList}")
        return []
    ven = venList[0]
    logging.debug(f"getUnionOfTargets(): ven={ven}")
    targets = ven.targets
    # find union of targets allocated to VEN via ven object and target_type, target_values
    allowed_targets = util.getMatchedTargets(targets, target_type, target_values)
    return allowed_targets

def getAllowedTargets(request):
    # get targets of ven object with client_id associated with requestor's token
    client_id = util.getClientId(request)
    vens = objStore.search_all("VEN")
    venList = [ven for ven in vens if ven.client_id == client_id]
    if 0 == len(venList) < 2:
        logging.warning(f"vens_controller.allowedTargets(): none or multiple vens with client_id {client_id} venList={venList}")
        return []
    ven = venList[0]
    logging.debug(f"getAllowedTargets(): ven={ven}")
    return ven.targets