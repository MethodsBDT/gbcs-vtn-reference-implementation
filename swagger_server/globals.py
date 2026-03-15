
# MQTTC contains an instantiated MqttClient object,
#  which is used to publish notifications to topics
#  This is set in main(), and used in mqtt.notification()

global MQTTC

# DYNSEC contains a DynsecManager instance when dynsec is configured, else None
DYNSEC = None

# VEN_MQTT_CREDENTIALS maps ven_id -> {'username': str, 'password': str}
VEN_MQTT_CREDENTIALS = {}

# BL_MQTT_CREDENTIALS maps client_id -> {'username': str, 'password': str}
BL_MQTT_CREDENTIALS = {}

# VENS contains a dict of ven objects, keyed by client_id

VENS = {}
