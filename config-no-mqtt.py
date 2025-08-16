import os
import logging
import sys

# Server configuration
SERVER_IP = '0.0.0.0'
SERVER_PORT = 8080

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

# Control log level via ENV variable
LOG_LEVEL = int(os.getenv('LOG_LEVEL', logging.INFO))

logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)
logging.info(f"config:log level is working, log level = {LOG_LEVEL}")

# OIDC Authorization Provider
OIDC_AUTH_ENABLED = os.getenv('OIDC_AUTH_ENABLED', False)
OIDC_BASE_URL = os.getenv('OIDC_BASE_URL', 'https://test-tool.auth.us-east-1.amazoncognito.com')
OIDC_KNOWN_ISSUER = os.getenv('OIDC_KNOWN_ISSUER', 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_N5wIYtzuO')

# Storage Implementation
STORAGE_IMPLEMENTATION = os.getenv('STORAGE_IMPLEMENTATION', 'IN_MEMORY')  # Values: IN_MEMORY, IN_FILE
STORAGE_FILE_PATH = os.getenv('STORAGE_FILE_PATH', "./tmp/fileStorage.json")

#
# Notifier Support and Implementation
#
# Only reququred Notifier bindings is WEBHOOK, this is the minimum
NOTIFIER_BINDINGS = ['WEBHOOK']
# NOTIFIER_BINDINGS = ['MQTT', 'WEBHOOK']
#
# MQTT Notifier binding configuration
#
# MQTT Broker Configuration
#
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
MQTT_TOPIC_BASE_VEN_EVENTS = 'events/vens'
