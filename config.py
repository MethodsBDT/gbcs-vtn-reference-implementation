import os
import logging
import sys

# Server configuration
SERVER_IP = '0.0.0.0'
SERVER_PORT = 8080
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# OIDC Authorization Provider
OIDC_AUTH_ENABLED = os.getenv('OIDC_AUTH_ENABLED', False)
OIDC_BASE_URL = os.getenv('OIDC_BASE_URL', 'https://test-tool.auth.us-east-1.amazoncognito.com')
OIDC_KNOWN_ISSUER = os.getenv('OIDC_KNOWN_ISSUER', 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_N5wIYtzuO')

# Storage Implementation
STORAGE_IMPLEMENTATION = os.getenv('STORAGE_IMPLEMENTATION', 'IN_FILE')  # Values: IN_MEMORY, IN_FILE
STORAGE_FILE_PATH = os.getenv('STORAGE_FILE_PATH', "./tmp/fileStorage.json")

AUTH_BASIC_VEN_CLIENT_ID = os.getenv('AUTH_BASIC_VEN_CLIENT_ID', 'ven_client')
AUTH_BASIC_VEN_SECRET = os.getenv('AUTH_BASIC_VEN_SECRET', '999')
AUTH_BASIC_VEN2_CLIENT_ID = os.getenv('AUTH_BASIC_VEN2_CLIENT_ID', 'ven_client2')
AUTH_BASIC_VEN2_SECRET = os.getenv('AUTH_BASIC_VEN2_SECRET', '9999')
AUTH_BASIC_BL_CLIENT_ID = os.getenv('AUTH_BASIC_BL_CLIENT_ID', 'bl_client')
AUTH_BASIC_BL_SECRET = os.getenv('AUTH_BASIC_BL_SECRET', '1001')

NOTIFIER_BINDINGS = ['WEBHOOK', 'MQTT']

MQTT_VTN_BROKER_IP = '0.0.0.0'
MQTT_VTN_BROKER_PORT = 1883
MQTT_CLIENT_BROKER_FQDN = '127.0.0.1'
MQTT_CLIENT_BROKER_PORT = 1883
MQTT_BROKER_CLIENT_ID = 'OpenADR3-VTN-RI'
# Currently the only serialization supported is JSON
MQTT_SERIALIZATION = 'JSON'
# MQTT_BROKER_AUTH one of 'ANONYMOUS', 'OAUTH2_BEARER_TOKEN', 'CERTIFICATE'
# The VTN RI currently supports only ANONYMOUS
MQTT_BROKER_AUTH = 'ANONYMOUS'
# The VTN RI doesn't currently implement/support CERTIFICATE authorization
# MQTT_BROKER_CLIENT_CERTS = {'ca_crt': '', 'client_crt': '', 'client_key': ''}
MQTT_BROKER_CLIENT_CERTS = None
#
# MQTT Binding Topic Base Paths
#
MQTT_TOPIC_BASE_PROGRAMS = 'programs'
MQTT_TOPIC_BASE_PROGRAM_EVENTS = 'events/programs'
MQTT_TOPIC_BASE_EVENTS = 'events'
MQTT_TOPIC_BASE_REPORTS = 'reports'
MQTT_TOPIC_BASE_RESOURCES = 'resources'
MQTT_TOPIC_BASE_SUBSCRIPTIONS = 'subscriptions'
MQTT_TOPIC_BASE_VENS = 'vens'
MQTT_TOPIC_BASE_VEN_RESOURCES = 'resources/vens'
MQTT_TOPIC_BASE_VEN_PROGRAMS = 'programs/vens'
MQTT_TOPIC_BASE_VEN_EVENTS = 'events/vens'