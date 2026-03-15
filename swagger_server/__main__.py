#!/usr/bin/env python3

import gevent.monkey
gevent.monkey.patch_all()

import connexion
import logging

from swagger_server import encoder, mqtt, globals
from gevent.pywsgi import WSGIServer, WSGIHandler
from config import SERVER_IP, SERVER_PORT, NOTIFIER_BINDINGS, MQTT_VTN_BROKER_IP, MQTT_VTN_BROKER_PORT, MQTT_BROKER_CLIENT_ID


class CloseConnectionHandler(WSGIHandler):
    """Force Connection: close on every response to prevent keep-alive connection accumulation."""
    close_connection = True


def main():
    # MQTTC is a global needed by others, AFAICT this is the only way they can get it...

    if ('MQTT' in NOTIFIER_BINDINGS) and MQTT_VTN_BROKER_IP and MQTT_VTN_BROKER_PORT:
        # Instantiate MqttClient
        try:
            globals.MQTTC = mqtt.MqttClient(client_id=MQTT_BROKER_CLIENT_ID,
                                            endpoint=MQTT_VTN_BROKER_IP,
                                            port=MQTT_VTN_BROKER_PORT)
            globals.MQTTC.start()
            logging.info(f"main(), Instantiated MqttClient, client_id={MQTT_BROKER_CLIENT_ID}, endpoint={MQTT_VTN_BROKER_IP}, port={MQTT_VTN_BROKER_PORT}")
        except:
            logging.warning(f"main(), exception instantiating MqttClient", exc_info=True)
    else:
        logging.info(f"main(), no MQTT broker instantiated, client_id={MQTT_BROKER_CLIENT_ID}, endpoint={MQTT_VTN_BROKER_IP}, port={MQTT_VTN_BROKER_PORT}")

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml',
                base_path='/openadr3/3.1.0',
                arguments={'title': 'OpenADR REST Demand Response API'},
                pythonic_params=True)
    # Note that the OpenADR3 protocol can run on any path; we're choosing to run it
    # on /openadr3/3.1.0.
    http_server = WSGIServer((SERVER_IP, SERVER_PORT), app, handler_class=CloseConnectionHandler)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
