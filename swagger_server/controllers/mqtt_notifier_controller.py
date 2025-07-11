import connexion
import six

from swagger_server.models.notifier_topics_response import NotifierTopicsResponse  # noqa: E501
from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server import util


def list_all_mqtt_notifier_topics_events():  # noqa: E501
    """List all MQTT binding topic names for operations on all events 

    List all MQTT binding topic names for operations on all events  # noqa: E501


    :rtype: NotifierTopicsResponse
    """
    return 'do some magic!'


def list_all_mqtt_notifier_topics_program(program_id):  # noqa: E501
    """List all MQTT binding topic names for operations on a program 

    List all MQTT binding topic names for operations on a program  # noqa: E501

    :param program_id: objectID of the program object
    :type program_id: dict | bytes

    :rtype: NotifierTopicsResponse
    """
    if connexion.request.is_json:
        program_id = ObjectID.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_all_mqtt_notifier_topics_program_events(program_id):  # noqa: E501
    """List all MQTT binding topic names for operations on events for a program 

    List all MQTT binding topic names for operations on events for a program  # noqa: E501

    :param program_id: Object ID of the program object
    :type program_id: dict | bytes

    :rtype: NotifierTopicsResponse
    """
    if connexion.request.is_json:
        program_id = ObjectID.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_all_mqtt_notifier_topics_programs():  # noqa: E501
    """List all MQTT notifier topic names for operations on programs 

    List all MQTT notifier topic names for operations on programs  # noqa: E501


    :rtype: NotifierTopicsResponse
    """
    return 'do some magic!'


def list_all_mqtt_notifier_topics_reports():  # noqa: E501
    """List all MQTT binding topic names for operations on all reports 

    List all MQTT binding topic names for operations on all reports  # noqa: E501


    :rtype: NotifierTopicsResponse
    """
    return 'do some magic!'


def list_all_mqtt_notifier_topics_resources():  # noqa: E501
    """List all MQTT binding topic names for operations on resources 

    List all MQTT binding topic names for operations on resources  # noqa: E501


    :rtype: NotifierTopicsResponse
    """
    return 'do some magic!'


def list_all_mqtt_notifier_topics_subscriptions():  # noqa: E501
    """List all MQTT binding topic names for operations on all subscriptions 

    List all MQTT binding topic names for operations on all subscriptions  # noqa: E501


    :rtype: NotifierTopicsResponse
    """
    return 'do some magic!'


def list_all_mqtt_notifier_topics_ven(ven_id):  # noqa: E501
    """List all MQTT binding topic names for operations on a ven 

    List all MQTT binding topic names for operations on a ven  # noqa: E501

    :param ven_id: venID of the vens object
    :type ven_id: dict | bytes

    :rtype: NotifierTopicsResponse
    """
    if connexion.request.is_json:
        ven_id = ObjectID.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_all_mqtt_notifier_topics_ven_events(ven_id):  # noqa: E501
    """List all MQTT binding topic names for operations on events targeted for a ven 

    List all MQTT binding topic names for operations on events targated for a ven  # noqa: E501

    :param ven_id: object ID of the ven object
    :type ven_id: dict | bytes

    :rtype: NotifierTopicsResponse
    """
    if connexion.request.is_json:
        ven_id = ObjectID.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_all_mqtt_notifier_topics_ven_programs(ven_id):  # noqa: E501
    """List all MQTT binding topic names for operations on programs targeted for a ven 

    List all MQTT binding topic names for operations on programs targeted for a ven  # noqa: E501

    :param ven_id: object ID of the ven object
    :type ven_id: dict | bytes

    :rtype: NotifierTopicsResponse
    """
    if connexion.request.is_json:
        ven_id = ObjectID.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_all_mqtt_notifier_topics_ven_resources(ven_id):  # noqa: E501
    """List all MQTT binding topic names for operations on resources for a ven 

    List all MQTT binding topic names for operations on resources for a ven  # noqa: E501

    :param ven_id: object ID of the ven object
    :type ven_id: dict | bytes

    :rtype: NotifierTopicsResponse
    """
    if connexion.request.is_json:
        ven_id = ObjectID.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_all_mqtt_notifier_topics_vens():  # noqa: E501
    """List all MQTT binding topic names for operations on vens 

    List all MQTT binding topic names for operations on vens  # noqa: E501


    :rtype: NotifierTopicsResponse
    """
    return 'do some magic!'
