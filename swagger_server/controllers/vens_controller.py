import connexion
from datetime import datetime, timezone
from http import HTTPStatus
import logging
from flask import request

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.models.bl_ven_request import BlVenRequest  # noqa: E501
from swagger_server.models.ven_ven_request import VenVenRequest  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server.objStore.storageInterface import objStore
from swagger_server import objectUtils

def create_ven(body):  # noqa: E501
    """create ven

    Create a new ven. # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: Ven
    """
    logging.info(f"create_ven(): ")

    targets = []
    if body["objectType"] in "VEN_VEN_REQUEST":
        venBody = VenVenRequest.from_dict(connexion.request.get_json())  # noqa: E501
        client_id = objectUtils.getClientId(request)
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

    now = datetime.now(timezone.utc)
    current_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    ven = Ven(
        created_date_time=current_time,
        modification_date_time=current_time,
        object_type='VEN',
        ven_name=venBody.ven_name,
        attributes=venBody.attributes,
        client_id=client_id,
        targets=targets
    )

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

    # VEN can only read ven objects with client_id matching client_id associated with it's token
    if objectUtils.getClientRole(request) in 'VEN':
        client_id = objectUtils.getClientId(request)
        if ven.client_id != client_id:
            return [], HTTPStatus.OK

    subscription_callback("VEN", "READ", ven)

    return ven, HTTPStatus.OK

def search_vens(ven_name=None, targets=None, skip=None, limit=None):  # noqa: E501
    """search vens

    List all vens. May filter results by venName as query param. May filter results by targets params. Use skip and pagination query params to limit response size.  # noqa: E501

    :param ven_name: Indicates ven objects w venName
    :type ven_name: dict | bytes
    :param targets: Indicates targets
    :type targets: list | bytes
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Ven]
    """
    logging.info(
        f"search_vens(): ven_name={ven_name} targets={targets} skip={skip} limit={limit}")

    vens = objStore.search_all("VEN")
    logging.debug(f"search_vens(): vens={vens}")
    if type(vens) is not list:
        status = vens
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_vens(): problem={problem}")
        return problem, status

    logging.info(f"search_vens(): vens={vens}")
    objects = objectList = vens

    # A VEN can only fetch a ven with a client_id matching the request token client_id
    if objectUtils.getClientRole(request) in 'VEN':
        client_id = objectUtils.getClientId(request)
        # There can ony be one ven with a given client_id
        objectList = [ven for ven in objectList if ven.client_id == client_id]
        if len(objectList) > 1:
            logging.warning(f"search_vens(): multiple vens with same client_id={client_id}")
        return objectList, HTTPStatus.OK

    # Request is from BL client
    if ven_name != None:
        objectList = [ven for ven in vens if ven.ven_name == ven_name]
        if len(objectList) == 0:
            return [], HTTPStatus.OK
        else:
            return objectList, HTTPStatus.OK

    # BL will fetch all objects if targets are not specified in query, or objects matching targets if present in query
    if targets != None:
        objectList = objectUtils.getObjectsWithTargets(objects, targets)

    if skip != None:
        if len(objectList) < skip:
            return [], HTTPStatus.OK
        objectList = objectList[skip:]
    if limit != None:
        objectList = objectList[:limit]

    logging.debug(f"search_vens(): objectList={objectList}")

    subscription_callback("VEN", "READ", objectList)

    return objectList, HTTPStatus.OK

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
        if venBody is None:
            problem = Problem(title="Bad Request: No request body", status="400")
            logging.warning(f"update_ven(): problem={problem}")
            return problem, HTTPStatus.BAD_REQUEST
        client_id = objectUtils.getClientId(request)
        targets = []
    else:
        venBody = BlVenRequest.from_dict(connexion.request.get_json())
        if venBody is None:
            problem = Problem(title="Bad Request: No request body", status="400")
            logging.warning(f"update_ven(): problem={problem}")
            return problem, HTTPStatus.BAD_REQUEST
        client_id = venBody.client_id  # noqa: E501
        if venBody.targets is not None:
            targets = venBody.targets
        else:
            targets = []

    ven, status = search_ven_by_id(ven_id)
    if ven is None or status == HTTPStatus.NOT_FOUND:
        problem = Problem(title="Not Found: program_id not found", status=HTTPStatus.NOT_FOUND)
        logging.warning(f"update_ven(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND
    if client_id != ven.client_id:
        problem = Problem(title="Forbidden: client_id of request does not match object", status="403")
        logging.warning(f"update_ven(): problem={problem}")
        return problem, HTTPStatus.FORBIDDEN

    # set modification date time
    now = datetime.now(timezone.utc)
    current_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    ven.modification_date_time = current_time

    ven.ven_name = venBody.ven_name
    ven.attributes = venBody.attributes
    ven.targets = targets

    ven = objStore.update("VEN", ven)
    if type(ven) is not Ven:
        status = ven
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_ven(): problem={problem}")
        return problem, status

    subscription_callback("VEN", "UPDATE", ven)
    return ven, HTTPStatus.OK

