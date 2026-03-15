import logging

import paho.mqtt.client as mqtt
import paho.mqtt.matcher as matcher
from pprint import pformat
from typing import Any, Callable, Union, Dict, List, Set

import json
from swagger_server.models.mqtt_notifier_binding_object import MqttNotifierBindingObject
from swagger_server.models.mqtt_notifier_authentication_anonymous import MqttNotifierAuthenticationAnonymous
from swagger_server.models.mqtt_notifier_authentication_oauth2_bearer_token import MqttNotifierAuthenticationOauth2BearerToken
from swagger_server.models.mqtt_notifier_authentication_certificate import MqttNotifierAuthenticationCertificate
from config import MQTT_SERIALIZATION, \
    MQTT_CLIENT_BROKER_FQDN, MQTT_CLIENT_BROKER_PORT, MQTT_BROKER_AUTH, MQTT_BROKER_CLIENT_CERTS, \
    MQTT_TOPIC_BASE_PROGRAMS, MQTT_TOPIC_BASE_PROGRAM_EVENTS, MQTT_TOPIC_BASE_EVENTS, MQTT_TOPIC_BASE_REPORTS, MQTT_TOPIC_BASE_SUBSCRIPTIONS, \
    MQTT_TOPIC_BASE_VENS, MQTT_TOPIC_BASE_RESOURCES, \
    MQTT_TOPIC_BASE_VEN_RESOURCES, MQTT_TOPIC_BASE_VEN_PROGRAMS, MQTT_TOPIC_BASE_VEN_EVENTS
from swagger_server.notifiers import resolve_ven_ids_from_targets
from swagger_server import globals


class MqttClient:
    def __init__(
            self,
            client_id: str,
            endpoint: str,
            port: int,
            callback: Callable[[Union[bytes,bytearray], Any], None] = None,
            username = None,
            password = None
    ):
        self.client_id = client_id
        self.mqttc = mqtt.Client(self.client_id)
        self.mqttc.reconnect_delay_set(min_delay=1, max_delay=30)
        self.mqttc.on_connect = self._on_connect
        self.mqttc.on_disconnect = self._on_disconnect
        self.mqttc.on_message = self._on_message
        self.mqttc.user_data_set(callback)
        self.sub_callbacks = {}
        self.sub_matcher = matcher.MQTTMatcher()

        self.is_running = False
        if username and password:
            self.mqttc.username_pw_set(username, password)
        self.mqttc.connect(endpoint, port, keepalive=60)

    def start(self, blocking=False):
        self.is_running = True
        if blocking:
            self.mqttc.loop_forever()
        else:
            self.mqttc.loop_start()

    def stop(self):
        self.is_running = False
        self.mqttc.disconnect()
        self.mqttc.loop_stop()

    def publish(self, topic: str, data: str, qos: int = 1, retain: bool = False):
        msg_info = self.mqttc.publish(topic, data, qos, retain)

        if msg_info.rc != mqtt.MQTT_ERR_SUCCESS:
            logging.warning(f"reason=mqttPublishFail,client={self.client_id},topic={topic}")

    def subscribe(self, sub: str, param: Any, qos: int = 1):
        self.sub_callbacks[sub] = (param, qos)
        self.sub_matcher[sub] = sub
        self.mqttc.subscribe(sub, qos)

    def _on_connect(self, mqttc: mqtt.Client, userdata: Any, flags: int, rc: int):
        logging.info(f"reason=mqttBrokerConnected,client={self.client_id}")

        for sub, (_, qos) in self.sub_callbacks.items():
            (result, msg_id) = self.mqttc.subscribe(sub, qos)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"reason=mqttSubscribeSuccess,client={self.client_id},sub={sub}")
            else:
                logging.warning(f"reason=mqttSubscribeFail,client={self.client_id},sub={sub}")

    def _on_disconnect(self, mqttc: mqtt.Client, userdata: Any, rc: int):
        if self.is_running and rc != mqtt.MQTT_ERR_SUCCESS:
            logging.warning(f"reason=mqttBrokerConnectionLost,client={self.client_id}")
        else:
            logging.info(f"reason=mqttBrokerDisconnected,client={self.client_id}")

    def _find_matching_sub(self, topic):
        try:
            return next(self.sub_matcher.iter_match(topic))
        except StopIteration:
            return None

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        try:
            sub = self._find_matching_sub(msg.topic)
        except:
            logging.warning(f"reason=onMessageFindMatchingSubException,topic={msg.topic}", exc_info=True)
            return

        if sub is None:
            logging.warning(f"reason=onMessageNoMatchingSubscription,topic={msg.topic}")
            return

        try:
            if userdata:
                userdata(msg.topic, msg.payload, self.sub_callbacks[sub][0])
            else:
                self.sub_callbacks[sub][0](msg.topic, msg.payload)
        except:
            logging.warning(f"reason=onMessageClientCallbackException,topic={msg.topic}", exc_info=True)


def binding(mqtt_username=None, mqtt_password=None):
    """
    Returns a MqttBindingObject, or None.
    When mqtt_username/mqtt_password are provided, includes credentials in the binding.
    """
    if MQTT_CLIENT_BROKER_FQDN and MQTT_CLIENT_BROKER_PORT and MQTT_BROKER_AUTH:
        if MQTT_CLIENT_BROKER_PORT == 1883:
            uri_schema = 'mqtt://'
        elif MQTT_CLIENT_BROKER_PORT == 8883:
            url_schema = 'mqtts://'
        # TODO: else error!
        # TODO: Handle nonstandard port
        connection_uri = uri_schema + MQTT_CLIENT_BROKER_FQDN
        if MQTT_SERIALIZATION:
            serialization = MQTT_SERIALIZATION
        else:
            serialization = 'JSON'
        if MQTT_BROKER_AUTH == 'ANONYMOUS':
            return MqttNotifierBindingObject(
                uris=[connection_uri],
                serialization=serialization,
                authentication=MqttNotifierAuthenticationAnonymous('ANONYMOUS'))
        elif MQTT_BROKER_AUTH == 'OAUTH2_BEARER_TOKEN':
            username = mqtt_username or 'oauth2'
            auth = MqttNotifierAuthenticationOauth2BearerToken(
                'OAUTH2_BEARER_TOKEN',
                username=username,
                password=mqtt_password)
            return MqttNotifierBindingObject(
                uris=[connection_uri],
                serialization=serialization,
                authentication=auth)
        elif MQTT_BROKER_AUTH == 'CERTIFICATE':
            return MqttNotifierBindingObject(
                uris=[connection_uri],
                serialization=serialization,
                authentication=MqttNotifierAuthenticationCertificate(
                    'CERTIFICATE',
                    ca_cert='dummy',
                    client_cert='dummy',
                    client_key='dummy'))
        else:
            logging.warning(f"mqtt.binding(), Unhandled authentication method, method={MQTT_BROKER_AUTH}")
            return None
    else:
        logging.warning(f"mqtt.binding(), No MQTT broker configured, FQDN={MQTT_CLIENT_BROKER_FQDN}, Port={MQTT_CLIENT_BROKER_PORT}")
        return None


def path(base_path: str, operation: str, id: str = None) -> str:
    """
    Returns string representing a topic path
    """
    if id:
        return base_path + '/' + id + '/' + operation
    else:
        return base_path + '/' + operation


def serialize(d: Dict) -> Any:
    """
    Creates the serialized message, only JSON supported for now!
    """
    if MQTT_SERIALIZATION == 'JSON':
        # TODO: Handle serialization exceptions
        return json.dumps(d)
    else:
        logging.warning(f"mqtt.serialize(), Unsupported MQTT_SERIALIZATION: {MQTT_SERIALIZATION}")


def get_targets(notification_object: Dict) -> Set:
    """
    .get(targets) often returns None, so this is a workaround
    """
    targets = notification_object.get('targets', None)
    if targets:
        return set(targets)
    else:
        return set()


def untargeted_object_type_topic_names(object_id: str,
                                       base_topic_untargeted: str,
                                       base_topic_untargeted_id: str,
                                       operation: str,
                                       notification_object: Dict) -> List:
    """
    Returns list of topic names
    """
    logging.debug(f"reason=untargetedObjectTypeTopicNames,id={object_id},object={notification_object}")
    return [path(base_topic_untargeted, operation),
            path(base_topic_untargeted_id, operation, notification_object.get(object_id))]


def targetable_object_type_topic_names(object_id: str,
                                       base_topic_untargeted: str,
                                       base_topic_untargeted_id: str,
                                       base_topic_targeted: str,
                                       operation: str,
                                       notification_object: Dict) -> List:
    """
    Returns list of topic names
    """
    targets = get_targets(notification_object)
    if targets:
        resolved_targets_ven_ids = resolve_ven_ids_from_targets(targets)
        logging.debug(f"reason=resolvedTargetsVenIds,value={resolved_targets_ven_ids}")
        if resolved_targets_ven_ids:
            topics = []
            for ven_id in resolved_targets_ven_ids:
                topics.append(path(base_topic_targeted, operation, ven_id))
            return topics
        # Targets present but no VENs resolved — fall back to untargeted delivery
        logging.debug(f"reason=targetsUnresolved,targets={targets},fallingBackToUntargeted")

    return untargeted_object_type_topic_names(object_id,
                                              base_topic_untargeted,
                                              base_topic_untargeted_id,
                                              operation,
                                              notification_object)


def topic_names(resourceName: str, operation: str, notification: Dict) -> List:
    """
    Returns list of topic names for which to publish the notification
    """
    notification_object = notification.get('object', None)
    if notification_object is None:
        # This should not happen
        return []
    if resourceName == 'PROGRAM':
        return targetable_object_type_topic_names('id',
                                                  MQTT_TOPIC_BASE_PROGRAMS,
                                                  MQTT_TOPIC_BASE_PROGRAMS,
                                                  MQTT_TOPIC_BASE_VEN_PROGRAMS,
                                                  operation,
                                                  notification_object)
    elif resourceName == 'EVENT':
        return targetable_object_type_topic_names('programID',
                                                  MQTT_TOPIC_BASE_EVENTS,
                                                  MQTT_TOPIC_BASE_PROGRAM_EVENTS,
                                                  MQTT_TOPIC_BASE_VEN_EVENTS,
                                                  operation,
                                                  notification_object)
    elif resourceName == 'VEN':
        return untargeted_object_type_topic_names('id',
                                                  MQTT_TOPIC_BASE_VENS,
                                                  MQTT_TOPIC_BASE_VENS,
                                                  operation,
                                                  notification_object)
    elif resourceName == 'RESOURCE':
        return untargeted_object_type_topic_names('venID',
                                                  MQTT_TOPIC_BASE_RESOURCES,
                                                  MQTT_TOPIC_BASE_VEN_RESOURCES,
                                                  operation,
                                                  notification_object)
    elif resourceName == 'REPORT':
        return [path(MQTT_TOPIC_BASE_REPORTS, operation)]
    elif resourceName == 'SUBSCRIPTION':
        return [path(MQTT_TOPIC_BASE_SUBSCRIPTIONS, operation)]
    else:
        logging.warning(f"mqtt.topic_names(), Unsupported resource: {resourceName}, operation: {operation}")
        return []


def notification(resourceName: str, operationUpper: str, notification: Dict):
    """
    Publish the notification to MQTT
    """
    MQTTC = globals.MQTTC

    if not MQTTC:
        logging.warning(f"mqtt.notification(): No MQTT Connection!")
        return
    # We have a connection, so proceed
    operation = operationUpper.lower()
    notification_object = notification.get('object', {})
    notification_object_id = notification_object.get('id', None)
    logging.debug(f"reason=mqttNotification,object_type={resourceName},id={notification_object_id},operation={operation},notification=\n{pformat(notification)}")
    # Publish the notification
    serialized_notification = serialize(notification)
    # Publish objects with an associated ID
    for topic_name in topic_names(resourceName, operation, notification):
        MQTTC.publish(topic=topic_name,
                      data=serialized_notification,
                      retain=True)
