import datetime

import six
import typing
from swagger_server import type_util
from flask import request
import logging

from swagger_server.controllers.authorization_controller import check_oAuth2ClientCredentials, validate_scope_oAuth2ClientCredentials  # noqa: E501
from swagger_server.services.auth.auth_provider import AuthServiceProvider
from swagger_server.objStore.storageInterface import objStore

auth_provider = AuthServiceProvider()

def getObjectsNoTargets(objects):
    # return objects that are untargeted
    # logging.info(f"getObjectsNoTargets(): objects={objects}")
    objectList = []
    for object in objects:
        if object.targets is None:
            objectList.append(object)

    logging.info(f"getObjectsNoTargets(): objectList={objectList}")
    return objectList


def getObjectsWithTargets(objects, targets):
    # return objects whose targets match targets
    logging.info(f"getObjectsWithTargets(): objects={objects} targets={targets}")

    if targets is None:
        return objects

    objectList = []
    for object in objects:
        if object.targets is None:
            continue
        for t in targets:
            # if any target string in query matches any target in object, there is a match
            if t in object.targets:
                objectList.append(object)
                break

    return objectList


def getClientId(request):
    # fetch client_id from request's bearer token

    auth_header = request.headers.get('Authorization')
    if auth_header:
        token_type, token_value = auth_header.split(' ', 1)
        if token_type.lower() == 'bearer':
            client_id = auth_provider.get_client_id(token_value)
            return client_id
    return None


def getClientRole(request):
    # infer BL or VEN client role from scopes associated with request's bearer token

    auth_header = request.headers.get('Authorization')
    if auth_header:
        token_type, token_value = auth_header.split(' ', 1)
        if token_type.lower() == 'bearer':
            token_scopes = check_oAuth2ClientCredentials(token_value)
            if validate_scope_oAuth2ClientCredentials(['bl_scope'], token_scopes["scopes"]):
                return 'BL'
            else:
                return 'VEN'
    return None


def getAllowedTargets(client_id):
    # get targets of ven object with client_id associated with requestor's token, and targets of associated resources
    # Returns None when VEN has no explicit targets (meaning all targets are allowed)
    # Returns a list of targets when VEN or its resources have targets
    vens = objStore.search_all("VEN")
    venList = [ven for ven in vens if ven.client_id == client_id]
    if 0 == len(venList) or len(venList) > 1:
        logging.warning(f"getAllowedTargets(): none or multiple vens with client_id {client_id} venList={venList}")
        return None
    ven = venList[0]
    logging.debug(f"getAllowedTargets(): ven={ven}")

    targetsList = list(ven.targets) if ven.targets else []

    resources = objStore.search_all("RESOURCE")
    resourceList = [r for r in resources if r.client_id == client_id]
    for resource in resourceList:
        if resource.targets is not None:
            targetsList.extend(resource.targets)

    # If no targets found on VEN or its resources, return None to indicate unrestricted access
    if len(targetsList) == 0:
        return None

    return targetsList