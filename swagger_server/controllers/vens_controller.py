import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.target import Target  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server import util


# recall this is just a toy VTN
MAX_RESOURCES = 3
MAX_VENS = 3

vens = []
# always increments
venID = 0
# number of extant vens
venCount = 0

resources = [[] for _ in range(MAX_RESOURCES)]

# always increments
resourceIDs = [0] * MAX_RESOURCES
# number of extant resources per ven
resourceCounts = [0] * MAX_RESOURCES

def _get_ven_index(ven_id):
    for venIndex in range(0, MAX_VENS):
        if vens[venIndex].id == ven_id:
            break

    if venIndex == MAX_VENS - 1:
        logging.info(f"delete_ven_resource(): ven_id not found")

    return venIndex

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

    # find index in vens of ven_id
    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS - 1:
        return None

    logging.info(f"create_resource(): venIndex={venIndex}")

    global resourceCounts
    logging.info(f"create_resource(): resourceCounts={resourceCounts[venIndex]}")
    if resourceCounts[venIndex] >= MAX_RESOURCES:
        logging.debug(f"create_resource(): max resources already created")
        return None

    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_resource(): resourceBody={resourceBody}")
    if resourceBody is None:
        return []

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    # venID expected as element following vens/
    base_url = connexion.request.base_url.split('/')
    try:
        ven_index = base_url.index("vens")
        venID = base_url[ven_index + 1]
    except ValueError:
        problem = Problem(title="Path not as expected", status="400")
        logging.warning(f"create_resource(): problem={problem}")
        return problem, 400

    global resourceIDs
    venResource = Resource(
        id=str(resourceIDs[venIndex]),
        created_date_time=current_time,
        modification_date_time=None,
        resource_name=resourceBody.resource_name,
        ven_id = venID,
        attributes=resourceBody.attributes,
        target_values=resourceBody.target_values
    )

    resources[venIndex].append(venResource)

    # bump resource ID
    resourceIDs[venIndex] += 1
    resourceCounts[venIndex] += 1

    logging.info(f"create_resource(): venResource={venResource}")

    subscription_callback("RESOURCE", "POST", venResource)

    return venResource

def create_ven(body):  # noqa: E501
    """create ven

    Create a new ven. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Ven
    """
    logging.info(f"create_ven():")

    global venID
    global venCount
    logging.info(f"create_ven(): venID={venID} venCount={venCount}")
    # logging.info(f"create_ven(): vens={vens}  resources[venCount]={resources[venCount]}")
    if venCount >= MAX_VENS:
        logging.debug(f"create_ven(): max vens already created")
        return None

    venBody = None
    if connexion.request.is_json:
        venBody = Ven.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_ven(): venBody={venBody}")
    if venBody is None:
        return []

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    ven = Ven(
        id=str(venID),
        created_date_time=current_time,
        modification_date_time=None,
        ven_name=venBody.ven_name,
        attributes=venBody.attributes,
        target_values=venBody.target_values,
        resources=venBody.resources
    )

    # bump ven ID
    venID += 1
    venCount += 1

    vens.append(ven)
    logging.debug(f"create_ven(): ven={ven}")
    logging.info(f"create_ven(): vens={vens}")

    subscription_callback("VEN", "POST", ven)

    return ven


def delete_ven(ven_id):  # noqa: E501
    """delete  ven

    Delete the ven specified by venID specified in path. # noqa: E501

    :param ven_id: object ID of ven.
    :type ven_id: dict | bytes

    :rtype: Ven
    """
    logging.info(f"delete_ven(): ven_id={ven_id}")

    global venCount
    logging.info(f"delete_ven(): venCount={venCount}")
    if venCount == 0:
        logging.debug(f"delete_ven(): no vens in system")
        return None

    ven = next((ven for ven in vens if ven.id == ven_id), None)
    if ven is not None:
        vens.remove(ven)
        logging.debug(f"delete_ven(): ven={ven}")
        logging.info(f"delete_ven(): vens={vens}")

        subscription_callback("VEN", "DELETE", ven)

        venCount -= 1
        return ven
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_ven: problem={problem}")
        return problem, 404

def delete_ven_resource(ven_id, resource_id):  # noqa: E501
    """delete  ven resource

    Delete the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: object ID of the associated ven.
    :type ven_id: dict | bytes
    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes

    :rtype: Resource
    """
    logging.info(f"delete_resource():")

    # find index in vens of ven_id
    logging.info(f"delete_ven_resource(): resources={resources}")
    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS - 1:
        return None

    global resourceCounts
    logging.info(f"delete_ven_resource(): resourceCount={resourceCounts[venIndex]}")
    if resourceCounts[venIndex] == 0:
        logging.debug(f"delete_ven_resource(): no resources in system")
        return None

    venResource = next((venResource for venResource in resources[venIndex] if venResource.id == resource_id), None)

    if venResource is not None:
        resources[venIndex].remove(venResource)
        logging.debug(f"delete_ven_resource(): venResource={venResource}")

        subscription_callback("RESOURCE", "DELETE", venResource)

        resourceCounts[venIndex] -= 1
        return venResource
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_ven_resource: problem={problem}")
        return problem, 404

def search_ven_by_id(ven_id):  # noqa: E501
    """search vens by ID

    Return the ven specified by venID specified in path. # noqa: E501

    :param ven_id: object ID of ven.
    :type ven_id: dict | bytes

    :rtype: Ven
    """
    logging.info(f"search_ven_by_id(): ven_id={ven_id}")
    ven = next((ven for ven in vens if ven.id == ven_id), None)
    logging.debug(f"search_ven_by_id(): ven={ven}")

    return ven

def search_ven_resource_by_id(ven_id, resource_id):  # noqa: E501
    """search ven resources by ID

    Return the ven resource specified by venID and resourceID specified in path. # noqa: E501

    :param ven_id: object ID of the associated ven.
    :type ven_id: dict | bytes
    :param resource_id: object ID of the resource.
    :type resource_id: dict | bytes

    :rtype: Resource
    """
    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS - 1:
        return None

    logging.info(f"search_ven_resource_by_id(): ven_id={ven_id} venIndex={venIndex} resource_id={resource_id}")
    resource = next((resource for resource in resources[venIndex] if resource.id == resource_id), None)
    logging.debug(f"search_ven_resource_by_id(): resource={resource}")

    return resource

def search_ven_resources(ven_id, targets=None, skip=None, limit=None):  # noqa: E501
    """search ven resources

    Return the ven resources specified by venID specified in path. # noqa: E501

    :param ven_id: Numeric ID of ven.
    :type ven_id: dict | bytes
    :param targets: return resources that match requested targets
    :type targets: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: Resource
    """
    logging.info(f"search_ven_resources(): ven_id={ven_id}")

    venIndex = int(ven_id)  # Our Ids are incrementing numbers cast as strings
    return (resources[venIndex])

def search_vens(targets=None, skip=None, limit=None):  # noqa: E501
    """search vens

    List all vens. Use skip and pagination query params to limit response size.  # noqa: E501

    :param targets: return vens that match requested targets
    :type targets: list | bytes
     :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Ven]
    """
    logging.info(f"search_vens(): ")

    return (vens)

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
    if connexion.request.is_json:
        venBody = Ven.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_ven(): venBody={venBody}")
    if venBody is None:
        return None

    ven = next((ven for ven in vens if ven.id == ven_id), None)
    if ven is None:
        logging.debug(f"update_ven(): ven is None")
        return None

    vens.remove(ven)

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    ven.modification_date_time = current_time

    if venBody.ven_name is not None:
        ven.ven_name = venBody.ven_name
    if venBody.target_values is not None:
        ven.target_values = venBody.target_values
    if venBody.resources is not None:
        ven.resources = venBody.resources
    if venBody.attributes is not None:
        ven.attributes = venBody.attributes,

    vens.append(ven)

    subscription_callback("VEN", "PUT", ven)

    return ven

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

    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS - 1:
        return None
    
    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_ven_resource(): resourceBody={resourceBody}")
    if resourceBody is None:
        return []

    venResource = next((venResource for venResource in resources[venIndex] if venResource.id == resource_id), None)
    if venResource is not None:
        resources[venIndex].remove(venResource)

        # set modification date time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        venResource.modification_date_time = current_time

        if resourceBody.resource_name is not None:
            venResource.resource_name = resourceBody.resource_name
        if resourceBody.target_values is not None:
            venResource.target_values = resourceBody.target_values
        if resourceBody.attributes is not None:
            venResource.attributes = resourceBody.attributes,

        resources[int(ven_id)].append(venResource)
        logging.debug(f"update_ven_resource(): venResource={venResource}")

        subscription_callback("RESOURCE", "PUT", venResource)

        return (venResource)

    return None
