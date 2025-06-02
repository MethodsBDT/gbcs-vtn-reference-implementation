import datetime

import six
import typing
from swagger_server import type_util
from flask import request
import logging

from swagger_server.controllers.authorization_controller import check_oAuth2ClientCredentials, validate_scope_oAuth2ClientCredentials  # noqa: E501
from swagger_server.services.auth.auth_provider import AuthServiceProvider

auth_provider = AuthServiceProvider()

def _deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if klass in (int, float, str, bool, bytearray):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif type_util.is_generic(klass):
        if type_util.is_list(klass):
            return _deserialize_list(data, klass.__args__[0])
        if type_util.is_dict(klass):
            return _deserialize_dict(data, klass.__args__[1])
    else:
        return deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = data
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return an original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    if string is None:
      return None

    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    if string is None:
      return None

    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.swagger_types:
        return data

    for attr, attr_type in instance.swagger_types.items():
        if data is not None \
                and instance.attribute_map[attr] in data \
                and isinstance(data, (list, dict)):
            value = data[instance.attribute_map[attr]]
            setattr(instance, attr, _deserialize(value, attr_type))

    return instance


def _deserialize_list(data, boxed_type):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type)
            for sub_data in data]


def _deserialize_dict(data, boxed_type):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type)
            for k, v in data.items() }

def getObjectsNoTargets(objects):
    # return objects that are untargeted
    # logging.info(f"getTargets(): target_type={target_type} target_values={target_values} objects={objects}")
    # FS - TBD: replace below with target logic
    objectList = []

    for i in range(0, len(objects)):
        if objects[i].targets == None:
            objectList.append(objects[i])

    logging.info(f"getObjectsNoTargets(): objectList={objectList}")
    return objectList

def getObjectsWithTargets(objects, targets):
    # return objects whose targets match targets
    logging.debug(f"getObjectsWithTargets(): targets={targets}")

    objectList = []
    for target in targets:
        for i in range(0, len(objects)):
            if objects[i].targets != None:
                for j in range(0, len(objects[i].targets)):
                    if objects[i].targets[j].type == target.type:
                        for k in range(0, len(objects[i].targets[j].values)):
                            if objects[i].targets[j].values[k] in target.values:
                                objectList.append(objects[i])
            # else:
            #     objectList.append(objects[i])

    logging.info(f"getObjectsWithTargets(): objectList={objectList}")
    return objectList

def getObjectsWithTarget(objects, target_type, target_values):
    # return all objects unless target_type defined, then return objects that match target
    logging.debug(f"getObjectsWithTarget(): target_type={target_type} target_values={target_values} objects={objects}")

    objectList = objects
    if target_type != None:
        objectList=[]
        for i in range(0, len(objects)):
            if objects[i].targets != None:
                for j in range(0, len(objects[i].targets)):
                    if objects[i].targets[j].type == target_type:
                        for k in range(0, len(objects[i].targets[j].values)):
                            if objects[i].targets[j].values[k] in target_values:
                                objectList.append(objects[i])

    logging.info(f"getObjectsWithTarget(): objectList={objectList}")
    return objectList

def getObjectsWithTargetOrNone(objects, target_type, target_values):
    # return all objects that have no targets unless target_type defined, then return objects that match target
    logging.debug(f"getObjectsWithTargetOrNone(): target_type={target_type} target_values={target_values} objects={objects}")

    objectList = []
    if target_type != None:
        for i in range(0, len(objects)):
            if objects[i].targets != None:
                for j in range(0, len(objects[i].targets)):
                    if objects[i].targets[j].type == target_type:
                        for k in range(0, len(objects[i].targets[j].values)):
                            if objects[i].targets[j].values[k] in target_values:
                                objectList.append(objects[i])
    else:
        for i in range(0, len(objects)):
            if objects[i].targets == None:
                objectList.append(objects[i])

    return objectList

def getMatchedTargets(targets, target_type, target_values):
    # verify that targetType and targetValues exist within targets
    logging.debug(f"getMatchedTargets(): target_type={target_type} target_values={target_values} targets={targets}")
    matched_targets = []
    for target in targets:
        if target.type in target_type:
            for value in target.values:
                if value in target_values:
                    matched_targets.append(target)
    return matched_targets

def getObjects(objects, objectTypes):
    # find objects of a given type within subscriptions
    logging.debug(f"getObjects(): objects={objects} objectTypes={objectTypes}")
    if objectTypes != None:
        objectList=[]
        for i in range(0, len(objects)):
            if objects[i].object_operations != None:
                for j in range(0, len(objects[i].object_operations)):
                    if objects[i].object_operations[j].objects != None:
                        for k in range(0, len(objects[i].object_operations[j].objects)):
                            if objects[i].object_operations[j].objects[k] in objectTypes:
                                objectList.append(objects[i])
    else:
        objectList = objects

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

