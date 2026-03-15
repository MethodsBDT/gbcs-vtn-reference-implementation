"""
Configuration loader for the OpenADR 3 VTN Reference Implementation.

Reads config.yaml (if present), then applies environment variable overrides.
Exports the same module-level constants used by the rest of the codebase.
"""

import logging
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None


def _load_yaml(path):
    """Load YAML config file, return empty dict if not found or yaml unavailable."""
    if yaml is None:
        return {}
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def _get(cfg, dotted_key, env_var=None, default=None):
    """Get a value from nested dict using dotted key, with env var override."""
    if env_var and os.getenv(env_var) is not None:
        val = os.getenv(env_var)
        # Coerce to int if default is int
        if isinstance(default, int):
            try:
                return int(val)
            except ValueError:
                pass
        # Coerce to bool if default is bool
        if isinstance(default, bool):
            return val.lower() in ('true', '1', 'yes')
        return val

    keys = dotted_key.split('.')
    node = cfg
    for k in keys:
        if isinstance(node, dict):
            node = node.get(k)
        else:
            return default
    return node if node is not None else default


# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------

_CONFIG_PATH = os.getenv('VTN_CONFIG', 'config.yaml')
_cfg = _load_yaml(_CONFIG_PATH)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

SERVER_IP = _get(_cfg, 'server.host', 'SERVER_IP', '0.0.0.0')
SERVER_PORT = _get(_cfg, 'server.port', 'SERVER_PORT', 8080)

_log_level = _get(_cfg, 'server.log_level', 'LOG_LEVEL', 'INFO')
logging.basicConfig(stream=sys.stdout, level=getattr(logging, _log_level, logging.INFO))

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

STORAGE_IMPLEMENTATION = _get(_cfg, 'storage.implementation', 'STORAGE_IMPLEMENTATION', 'IN_FILE')
STORAGE_FILE_PATH = _get(_cfg, 'storage.file_path', 'STORAGE_FILE_PATH', './tmp/fileStorage.json')

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

_auth_provider = _get(_cfg, 'auth.provider', None, 'basic')
OIDC_AUTH_ENABLED = os.getenv('OIDC_AUTH_ENABLED', _auth_provider == 'oidc')
OIDC_BASE_URL = _get(_cfg, 'auth.oidc.base_url', 'OIDC_BASE_URL',
                      'https://test-tool.auth.us-east-1.amazoncognito.com')
OIDC_KNOWN_ISSUER = _get(_cfg, 'auth.oidc.known_issuer', 'OIDC_KNOWN_ISSUER',
                          'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_N5wIYtzuO')

# Auth clients — read from YAML list or fall back to env vars / defaults
_clients = _get(_cfg, 'auth.clients', None, None)

def _find_client(clients, role, index=0):
    """Find the nth client with the given role from the YAML clients list."""
    if not clients:
        return None, None
    matches = [c for c in clients if c.get('role') == role]
    if index < len(matches):
        return matches[index].get('id'), str(matches[index].get('secret'))
    return None, None

_ven1_id, _ven1_secret = _find_client(_clients, 'VEN', 0)
_ven2_id, _ven2_secret = _find_client(_clients, 'VEN', 1)
_bl_id, _bl_secret = _find_client(_clients, 'BL', 0)

AUTH_BASIC_VEN_CLIENT_ID = os.getenv('AUTH_BASIC_VEN_CLIENT_ID', _ven1_id or 'ven_client')
AUTH_BASIC_VEN_SECRET = os.getenv('AUTH_BASIC_VEN_SECRET', _ven1_secret or '999')
AUTH_BASIC_VEN2_CLIENT_ID = os.getenv('AUTH_BASIC_VEN2_CLIENT_ID', _ven2_id or 'ven_client2')
AUTH_BASIC_VEN2_SECRET = os.getenv('AUTH_BASIC_VEN2_SECRET', _ven2_secret or '9999')
AUTH_BASIC_BL_CLIENT_ID = os.getenv('AUTH_BASIC_BL_CLIENT_ID', _bl_id or 'bl_client')
AUTH_BASIC_BL_SECRET = os.getenv('AUTH_BASIC_BL_SECRET', _bl_secret or '1001')

# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

_bindings = _get(_cfg, 'notifications.bindings', None, None)
NOTIFIER_BINDINGS = _bindings if _bindings else ['WEBHOOK', 'MQTT']

# ---------------------------------------------------------------------------
# MQTT
# ---------------------------------------------------------------------------

MQTT_VTN_BROKER_IP = _get(_cfg, 'mqtt.broker.host', None, '0.0.0.0')
MQTT_VTN_BROKER_PORT = _get(_cfg, 'mqtt.broker.port', None, 1883)
MQTT_CLIENT_BROKER_FQDN = _get(_cfg, 'mqtt.broker.host', None, '127.0.0.1')
MQTT_CLIENT_BROKER_PORT = _get(_cfg, 'mqtt.broker.port', None, 1883)
MQTT_BROKER_CLIENT_ID = _get(_cfg, 'mqtt.broker.client_id', None, 'OpenADR3-VTN-RI')
MQTT_SERIALIZATION = _get(_cfg, 'mqtt.broker.serialization', None, 'JSON')
MQTT_BROKER_AUTH = _get(_cfg, 'mqtt.broker.auth', None, 'ANONYMOUS')
MQTT_BROKER_CLIENT_CERTS = _get(_cfg, 'mqtt.broker.certs', None, None)
MQTT_BROKER_USERNAME = _get(_cfg, 'mqtt.broker.username', 'MQTT_BROKER_USERNAME', None)
MQTT_BROKER_PASSWORD = _get(_cfg, 'mqtt.broker.password', 'MQTT_BROKER_PASSWORD', None)

# MQTT topic base paths
MQTT_TOPIC_BASE_PROGRAMS = _get(_cfg, 'mqtt.topics.programs', None, 'programs')
MQTT_TOPIC_BASE_PROGRAM_EVENTS = _get(_cfg, 'mqtt.topics.program_events', None, 'events/programs')
MQTT_TOPIC_BASE_EVENTS = _get(_cfg, 'mqtt.topics.events', None, 'events')
MQTT_TOPIC_BASE_REPORTS = _get(_cfg, 'mqtt.topics.reports', None, 'reports')
MQTT_TOPIC_BASE_RESOURCES = _get(_cfg, 'mqtt.topics.resources', None, 'resources')
MQTT_TOPIC_BASE_SUBSCRIPTIONS = _get(_cfg, 'mqtt.topics.subscriptions', None, 'subscriptions')
MQTT_TOPIC_BASE_VENS = _get(_cfg, 'mqtt.topics.vens', None, 'vens')
MQTT_TOPIC_BASE_VEN_RESOURCES = _get(_cfg, 'mqtt.topics.ven_resources', None, 'resources/vens')
MQTT_TOPIC_BASE_VEN_PROGRAMS = _get(_cfg, 'mqtt.topics.ven_programs', None, 'programs/vens')
MQTT_TOPIC_BASE_VEN_EVENTS = _get(_cfg, 'mqtt.topics.ven_events', None, 'events/vens')

# ---------------------------------------------------------------------------
# mDNS (future use)
# ---------------------------------------------------------------------------

MDNS_ENABLED = _get(_cfg, 'mdns.enabled', 'MDNS_ENABLED', False)
MDNS_SERVICE_NAME = _get(_cfg, 'mdns.service_name', 'MDNS_SERVICE_NAME', 'OpenADR3 VTN')

# ---------------------------------------------------------------------------
# Startup logging
# ---------------------------------------------------------------------------

_log = logging.getLogger(__name__)
_log.info(f"config: source={_CONFIG_PATH}, yaml={'loaded' if _cfg else 'not found (using defaults)'}")
_log.info(f"config: server={SERVER_IP}:{SERVER_PORT}, storage={STORAGE_IMPLEMENTATION}, auth={'oidc' if OIDC_AUTH_ENABLED else 'basic'}")
_log.info(f"config: notifications={NOTIFIER_BINDINGS}")
if 'MQTT' in NOTIFIER_BINDINGS:
    _log.info(f"config: mqtt broker={MQTT_CLIENT_BROKER_FQDN}:{MQTT_CLIENT_BROKER_PORT}, auth={MQTT_BROKER_AUTH}, client_id={MQTT_BROKER_CLIENT_ID}")
_log.info(f"config: auth clients=[{AUTH_BASIC_VEN_CLIENT_ID}, {AUTH_BASIC_VEN2_CLIENT_ID}, {AUTH_BASIC_BL_CLIENT_ID}]")
if MQTT_BROKER_USERNAME:
    _log.info(f"config: mqtt broker auth user={MQTT_BROKER_USERNAME}")
if MDNS_ENABLED:
    _log.info(f"config: mdns enabled, service_name={MDNS_SERVICE_NAME}")
