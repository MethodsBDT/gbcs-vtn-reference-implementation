"""
Mosquitto Dynamic Security plugin manager.

Manages broker users and ACLs at runtime by publishing commands to
$CONTROL/dynamic-security/v1 and receiving responses.
"""

import json
import logging
import secrets
import uuid

import gevent
import gevent.event

from swagger_server import globals
from config import MQTT_TOPIC_BASE_PROGRAMS, MQTT_TOPIC_BASE_PROGRAM_EVENTS, \
    MQTT_TOPIC_BASE_EVENTS, MQTT_TOPIC_BASE_REPORTS, \
    MQTT_TOPIC_BASE_SUBSCRIPTIONS, MQTT_TOPIC_BASE_VENS, MQTT_TOPIC_BASE_RESOURCES, \
    MQTT_TOPIC_BASE_VEN_RESOURCES, MQTT_TOPIC_BASE_VEN_PROGRAMS, MQTT_TOPIC_BASE_VEN_EVENTS

DYNSEC_COMMAND_TOPIC = '$CONTROL/dynamic-security/v1'
DYNSEC_RESPONSE_TOPIC = '$CONTROL/dynamic-security/v1/response'
DYNSEC_TIMEOUT = 5  # seconds


class DynsecManager:
    """Manages Mosquitto dynamic security clients and roles via the MQTT dynsec API."""

    def __init__(self, mqtt_client):
        self.mqttc = mqtt_client
        self._pending = {}  # correlationData -> gevent.event.AsyncResult
        # Subscribe to dynsec responses
        self.mqttc.subscribe(DYNSEC_RESPONSE_TOPIC, self._on_response)

    def _on_response(self, topic, payload):
        """Callback for dynsec response messages."""
        try:
            response = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            logging.warning(f"dynsec: unparseable response payload")
            return

        responses = response.get('responses', [])
        for resp in responses:
            corr = resp.get('correlationData')
            if corr and corr in self._pending:
                self._pending[corr].set(resp)

    def _send_command(self, command, **kwargs):
        """Send a single dynsec command and wait for response."""
        corr = str(uuid.uuid4())
        result = gevent.event.AsyncResult()
        self._pending[corr] = result

        cmd = {'command': command, 'correlationData': corr}
        cmd.update(kwargs)
        payload = json.dumps({'commands': [cmd]})

        self.mqttc.publish(DYNSEC_COMMAND_TOPIC, payload, qos=1)

        try:
            resp = result.get(timeout=DYNSEC_TIMEOUT)
        except gevent.Timeout:
            logging.warning(f"dynsec: timeout waiting for response to {command}")
            return None
        finally:
            self._pending.pop(corr, None)

        if resp.get('error'):
            logging.warning(f"dynsec: {command} error: {resp.get('error')}")
            return None
        return resp

    def _send_commands(self, commands):
        """Send multiple dynsec commands in a single message."""
        results = {}
        for cmd in commands:
            corr = str(uuid.uuid4())
            cmd['correlationData'] = corr
            results[corr] = gevent.event.AsyncResult()
            self._pending[corr] = results[corr]

        payload = json.dumps({'commands': commands})
        self.mqttc.publish(DYNSEC_COMMAND_TOPIC, payload, qos=1)

        responses = {}
        for corr, async_result in results.items():
            try:
                resp = async_result.get(timeout=DYNSEC_TIMEOUT)
                responses[corr] = resp
            except gevent.Timeout:
                logging.warning(f"dynsec: timeout waiting for batched command response")
                responses[corr] = None
            finally:
                self._pending.pop(corr, None)
        return responses

    def create_ven_client(self, ven_id):
        """
        Create a dynsec client for a VEN with appropriate roles.
        Returns {'username': str, 'password': str} or None on failure.
        """
        username = f"ven-{ven_id}"
        password = secrets.token_urlsafe(32)
        role_name = f"ven-{ven_id}"

        # Create the per-VEN role with VEN-specific topic ACLs
        acls = [
            {"acltype": "subscribePattern", "topic": f"{MQTT_TOPIC_BASE_VENS}/{ven_id}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{MQTT_TOPIC_BASE_VEN_RESOURCES}/{ven_id}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{MQTT_TOPIC_BASE_VEN_PROGRAMS}/{ven_id}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{MQTT_TOPIC_BASE_VEN_EVENTS}/{ven_id}/#", "priority": 0, "allow": True},
            {"acltype": "subscribePattern", "topic": f"{MQTT_TOPIC_BASE_PROGRAM_EVENTS}/+/#", "priority": 0, "allow": True},
        ]

        resp = self._send_command('createRole', rolename=role_name, acls=acls)
        if resp is None:
            logging.warning(f"dynsec: failed to create role {role_name}")
            return None

        # Create the client with ven-base and per-VEN roles
        resp = self._send_command('createClient',
                                  username=username,
                                  password=password,
                                  textname=f"VEN {ven_id}",
                                  roles=[
                                      {"rolename": "ven-base", "priority": 0},
                                      {"rolename": role_name, "priority": 0},
                                  ])
        if resp is None:
            logging.warning(f"dynsec: failed to create client {username}")
            # Clean up the role we just created
            self._send_command('deleteRole', rolename=role_name)
            return None

        creds = {'username': username, 'password': password}
        globals.VEN_MQTT_CREDENTIALS[ven_id] = creds
        logging.info(f"dynsec: created VEN client, ven_id={ven_id}, mqtt_user={username}")
        return creds

    def delete_ven_client(self, ven_id):
        """Delete the dynsec client and role for a VEN."""
        username = f"ven-{ven_id}"
        role_name = f"ven-{ven_id}"

        self._send_command('deleteClient', username=username)
        self._send_command('deleteRole', rolename=role_name)

        globals.VEN_MQTT_CREDENTIALS.pop(ven_id, None)
        logging.info(f"dynsec: deleted VEN client, ven_id={ven_id}, mqtt_user={username}")

    def set_client_password(self, username, password):
        """Set/reset a client's password."""
        return self._send_command('setClientPassword', username=username, password=password)

    def create_bl_client(self, username, password):
        """
        Create a dynsec client for a BL (Business Logic) subscriber.
        Returns {'username': str, 'password': str} or None on failure.
        """
        resp = self._send_command('createClient',
                                  username=username,
                                  password=password,
                                  textname=f"BL client {username}",
                                  roles=[
                                      {"rolename": "bl-subscriber", "priority": 0},
                                  ])
        if resp is None:
            logging.warning(f"dynsec: failed to create BL client {username}")
            return None

        logging.info(f"dynsec: created BL client, mqtt_user={username}")
        return {'username': username, 'password': password}

    def regenerate_ven_credentials(self, ven_id):
        """
        Regenerate MQTT password for an existing VEN.
        Used on VTN restart to refresh credentials without recreating the client.
        If the client doesn't exist yet, creates it from scratch.
        """
        username = f"ven-{ven_id}"
        password = secrets.token_urlsafe(32)

        resp = self.set_client_password(username, password)
        if resp is None:
            # Client may not exist (first start after enabling dynsec) — create it
            logging.info(f"dynsec: client {username} not found, creating")
            return self.create_ven_client(ven_id)

        creds = {'username': username, 'password': password}
        globals.VEN_MQTT_CREDENTIALS[ven_id] = creds
        logging.info(f"dynsec: regenerated credentials for ven_id={ven_id}")
        return creds
