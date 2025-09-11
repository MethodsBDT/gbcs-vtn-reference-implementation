
# MQTTC contains an instantiated MqttClient object,
#  which is used to publish notifications to topics
#  This is set in main(), and used in mqtt.notification()

global MQTTC

# VENS contains a dict of ven objects, keyed by client_id

VENS = {}
