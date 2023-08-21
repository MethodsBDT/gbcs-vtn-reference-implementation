import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.values_map import ValuesMap  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server import util


# recall this is just a toy VTN
MAX_RESOURCES = 3
MAX_VENS = 3

vens = []
# always increments
venID = 0
# always increments
resourceIDs = [0] * MAX_RESOURCES

def _get_ven_index(ven_id):
    logging.info(f"_get_ven_index(): ven_id={ven_id} vens={vens}")
    venIndex = MAX_VENS
    for index in range(0, len(vens)):
        # logging.info(f"_get_ven_index(): vens[venIndex]={vens[venIndex]}")
        if vens[index].id == ven_id:
            venIndex = index
            break
    logging.info(f"_get_ven_index(): venIndex={venIndex} ")

    return venIndex

def create_ven(body):  # noqa: E501
    """create ven

    Create a new ven. # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Ven
    """
    global venID
    logging.info(f"create_ven(): ")

    if len(vens) >= MAX_VENS:
        problem = Problem(title="Insufficient Storage", status="507")
        logging.warning(f"create_ven(): problem={problem}")
        return problem, 507

    venBody = None
    if connexion.request.is_json:
        venBody = Ven.from_dict(connexion.request.get_json())  # noqa: E501
    if venBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"create_ven(): problem={problem}")
        return problem, 400

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    ven = Ven(
        id=str(venID),
        created_date_time=current_time,
        modification_date_time=None,
        object_type='VEN',
        ven_name=venBody.ven_name,
        attributes=venBody.attributes,
        targets=venBody.targets
    )

    if venBody.resources is not None:
        ven.resources = venBody.resources
    else:
        ven.resources = []

    # bump ven ID
    venID += 1
    vens.append(ven)
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
    if len(vens) == 0:
        problem = Problem(title="Not Found: No vens in system", status="404")
        logging.warning(f"delete_ven(): problem={problem}")
        return problem, 404

    ven = next((ven for ven in vens if ven.id == ven_id), None)
    if ven is None:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_ven: problem={problem}")
        return problem, 404

    vens.remove(ven)
    subscription_callback("VEN", "DELETE", ven)
    return ven


def search_ven_by_id(ven_id):  # noqa: E501
    """search vens by ID

    Return the ven specified by venID specified in path. # noqa: E501

    :param ven_id: object ID of ven.
    :type ven_id: dict | bytes

    :rtype: Ven
    """
    logging.info(f"search_ven_by_id(): ven_id={ven_id}")
    ven = next((ven for ven in vens if ven.id == ven_id), None)
    if ven is None:
        problem = Problem(title="Not Found: ven_id not found", status="404")
        logging.warning(f"search_ven_by_id(): problem={problem}")
        return problem, 404

    subscription_callback("VEN", "GET", ven)

    return ven


def search_vens(target_type=None, target_values=None, skip=None, limit=None):  # noqa: E501
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
    logging.info(
        f"search_all_vens(): target_type={target_type} target_values={target_values} skip={skip} limit={limit}")

    logging.debug(f"search_all_vens(): vens={vens}")
    venList = util.getTargets(vens, target_type, target_values)
    if skip != None:
        if len(vens) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_vens(): problem={problem}")
            return problem, 404
        venList = vens[skip:]
    if limit != None:
        venList = venList[:limit]
    logging.debug(f"search_all_vens(): venList={venList}")

    subscription_callback("VEN", "GET", venList)

    return venList

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

    if venBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_ven(): problem={problem}")
        return problem, 400

    ven = next((ven for ven in vens if ven.id == ven_id), None)
    if ven is None:
        problem = Problem(title="Not Found: ven_id not found", status="404")
        logging.warning(f"update_ven(): problem={problem}")
        return problem, 404

    vens.remove(ven)

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    ven.modification_date_time = current_time

    if venBody.ven_name is not None:
        ven.ven_name = venBody.ven_name
    if venBody.targets is not None:
        ven.target = venBody.targets
    if venBody.resources is not None:
        ven.resources = venBody.resources
    if venBody.attributes is not None:
        ven.attributes = venBody.attributes,

    logging.debug(f"update_ven(): vens={vens}")
    vens.append(ven)
    subscription_callback("VEN", "PUT", ven)
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

    # find index in vens of ven_id
    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS:
        problem = Problem(title="Not Found: ven_id not found", status="404")
        logging.warning(f"create_resource(): problem={problem}")
        return problem, 404

    logging.info(f"create_resource(): venIndex={venIndex}")

    logging.info(f"create_resource(): len ven.resources={len(vens[venIndex].resources)}")
    if len(vens[venIndex].resources) >= MAX_RESOURCES:
        problem = Problem(title="Insufficient Storage", status="507")
        logging.warning(f"create_resource(): problem={problem}")
        return problem, 507

    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501
    if resourceBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"create_resource(): problem={problem}")
        return problem, 400

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    # venID expected as element following vens/
    # Note venId not same as venIndex into vens list
    base_url = connexion.request.base_url.split('/')
    ven_index = base_url.index("vens")
    venID = base_url[ven_index + 1]

    global resourceIDs
    logging.debug(f"create_resource(): resourceIDs={resourceIDs}")
    venResource = Resource(
        id=str(resourceIDs[venIndex]),
        created_date_time=current_time,
        modification_date_time=None,
        object_type='RESOURCE',
        resource_name=resourceBody.resource_name,
        ven_id = venID,
        attributes=resourceBody.attributes,
        targets=resourceBody.targets
    )

    vens[venIndex].resources.append(venResource)

    logging.debug(f"create_resource(): venResource={venResource}")
    logging.debug(f"create_resource(): vens[venIndex].resources={vens[venIndex].resources}")

    # bump resource ID
    resourceIDs[venIndex] += 1
    subscription_callback("RESOURCE", "POST", venResource)
    return venResource

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

    # find index in vens of ven_id
    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS:
        problem = Problem(title="Not Found: ven_id not found", status="404")
        logging.warning(f"delete_ven_resource(): problem={problem}")
        return problem, 404

    ven = vens[venIndex]
    logging.debug(f"delete_ven_resource(): venIndex={venIndex} ven={ven}")

    if len(ven.resources) == 0:
        problem = Problem(title="Not Found: no resources in system", status="404")
        logging.warning(f"delete_ven_resource(): problem={problem}")
        return problem, 404

    venResource = next((venResource for venResource in ven.resources if venResource.id == resource_id), None)
    if venResource is None:
        problem = Problem(title="Not Found: resource_id not found", status="404")
        logging.warning(f"delete_ven_resource: problem={problem}")
        return problem, 404

    logging.debug(f"delete_ven_resource(): venResource={venResource}")
    logging.debug(f"delete_ven_resource(): ven.resources={ven.resources}")

    ven.resources.remove(venResource)
    subscription_callback("RESOURCE", "DELETE", venResource)
    return venResource

def search_ven_resources(ven_id, target_type=None, target_values=None, skip=None, limit=None):  # noqa: E501
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

    logging.info(
        f"search_all_ven_resources(): target_type={target_type} target_values={target_values} skip={skip} limit={limit}")

    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS:
        problem = Problem(title="Not Found: ven_id not found", status="404")
        logging.warning(f"search_ven_resources(): problem={problem}")
        return problem, 404

    ven = vens[venIndex]
    logging.debug(f"search_ven_resources(): venIndex={venIndex} ven={ven}")

    logging.debug(f"search_all_ven_resources(): ven.resources={ven.resources}")
    ven_resourceList = util.getTargets(ven.resources, target_type, target_values)
    if skip != None:
        if len(ven_resourceList) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_ven_resources(): problem={problem}")
            return problem, 404
        ven_resourceList = ven_resourceList[skip:]
    if limit != None:
        ven_resourceList = ven_resourceList[:limit]
    logging.debug(f"search_all_ven_resources(): ven_resourceList={ven_resourceList}")

    subscription_callback("RESOURCE", "GET", ven_resourceList)

    return ven_resourceList

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
    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS:
        problem = Problem(title="Not Found: ven_id not found", status="404")
        logging.warning(f"search_ven_resource_by_id(): problem={problem}")
        return problem, 404

    ven = vens[venIndex]
    logging.debug(f"search_ven_resource_by_id(): venIndex={venIndex} ven={ven}")

    if len(ven.resources) == 0:
        problem = Problem(title="Not Found: no resources in system", status="404")
        logging.warning(f"search_ven_resource_by_id(): problem={problem}")
        return problem, 404

    resource = next((resource for resource in ven.resources if resource.id == resource_id), None)
    if resource is None:
        problem = Problem(title="Not Found: resource_id not found", status="404")
        logging.warning(f"search_ven_resource_by_id(): problem={problem}")
        return problem, 404

    logging.debug(f"search_ven_resource_by_id(): resource={resource}")

    subscription_callback("RESOURCE", "GET", resource)

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

    venIndex = _get_ven_index(ven_id)
    if venIndex >= MAX_VENS:
        problem = Problem(title="Not Found: ven_id not found", status="404")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, 404

    ven = vens[venIndex]
    logging.debug(f"update_ven_resource(): venIndex={venIndex} ven={ven}")

    if len(ven.resources) == 0:
        problem = Problem(title="Not Found: no resources in system", status="404")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, 404
    
    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501

    if resourceBody is None:
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, 400

    venResource = next((venResource for venResource in ven.resources if venResource.id == resource_id), None)
    if venResource is None:
        problem = Problem(title="Not Found: resource_id not found", status="404")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, 404

    ven.resources.remove(venResource)

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    venResource.modification_date_time = current_time

    if resourceBody.resource_name is not None:
        venResource.resource_name = resourceBody.resource_name
    if resourceBody.targets is not None:
        venResource.targets = resourceBody.targets
    if resourceBody.attributes is not None:
        venResource.attributes = resourceBody.attributes,

    logging.debug(f"update_ven_resource(): venResource={venResource}")
    ven.resources.append(venResource)
    subscription_callback("RESOURCE", "PUT", venResource)
    return (venResource)
