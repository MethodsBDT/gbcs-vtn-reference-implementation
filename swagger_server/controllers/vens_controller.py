import connexion
from datetime import datetime
from http import HTTPStatus
import logging

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
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

    :param body: 
    :type body: dict | bytes

    :rtype: Ven
    """
    logging.info(f"create_ven(): ")

    venBody = None
    if connexion.request.is_json:
        venBody = Ven.from_dict(connexion.request.get_json())  # noqa: E501

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    ven = Ven(
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

    status = objStore.insert(ven)
    if status != HTTPStatus.CREATED:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_ven(): problem={problem}")
        return problem, status

    subscription_callback("VEN", "POST", ven)
    return ven, HTTPStatus.CREATED

def delete_ven(ven_id):  # noqa: E501
    """delete  ven

    Delete the ven specified by venID specified in path. # noqa: E501

    :param ven_id: object ID of ven.
    :type ven_id: dict | bytes

    :rtype: Ven
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

    subscription_callback("VEN", "GET", ven)

    return ven, HTTPStatus.OK

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

    vens = objStore.search_all("VEN")
    logging.debug(f"search_all_vens(): vens={vens}")
    if type(vens) is not list:
        status = vens
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_vens(): problem={problem}")
        return problem, status

    venList = util.getTargets(vens, target_type, target_values)
    if skip != None:
        if len(vens) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_vens(): problem={problem}")
            return problem, HTTPStatus.NOT_FOUND
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
    if venBody.targets is not None:
        ven.target = venBody.targets
    if venBody.resources is not None:
        ven.resources = venBody.resources
    if venBody.attributes is not None:
        ven.attributes = venBody.attributes,

    ven = objStore.update("VEN", ven)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_ven(): problem={problem}")
        return problem, status

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
    global resource_id

    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_resource(): problem={problem}")
        return problem, status

    if len(ven.resources) >= MAX_RESOURCES:
        status = HTTPStatus.INSUFFICIENT_STORAGE
        problem = Problem(title="Insufficient Storage ", status=str(status))
        logging.warning(f"create_resource(): problem={problem}")
        return problem, status

    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501

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
        targets=resourceBody.targets
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

    subscription_callback("RESOURCE", "POST", venResource)
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

    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_by_id(): problem={problem}")
        return problem, status

    logging.debug(f"search_all_ven_resources(): ven.resources={ven.resources}")
    ven_resourceList = util.getTargets(ven.resources, target_type, target_values)
    if skip != None:
        if len(ven_resourceList) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_ven_resources(): problem={problem}")
            return problem, HTTPStatus.NOT_FOUND
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

    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_by_id(): problem={problem}")
        return problem, status

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
    ven = objStore.search("VEN", ven_id)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_ven_by_id(): problem={problem}")
        return problem, status

    logging.debug(f"update_ven_resource(): ven={ven}")

    if len(ven.resources) == 0:
        problem = Problem(title="Not Found: no resources in system", status="404")
        logging.warning(f"update_ven_resource(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    resourceBody = None
    if connexion.request.is_json:
        resourceBody = Resource.from_dict(connexion.request.get_json())  # noqa: E501

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
    if resourceBody.targets is not None:
        venResource.targets = resourceBody.targets
    if resourceBody.attributes is not None:
        venResource.attributes = resourceBody.attributes,

    logging.debug(f"update_ven_resource(): venResource={venResource}")
    ven.resources.append(venResource)
    subscription_callback("RESOURCE", "PUT", venResource)
    return (venResource)
