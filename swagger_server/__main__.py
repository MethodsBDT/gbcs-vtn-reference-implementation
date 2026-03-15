#!/usr/bin/env python3

import gevent.monkey
gevent.monkey.patch_all()

import connexion
import logging

from swagger_server import encoder, mqtt, mdns, dynsec, globals
from gevent.pywsgi import WSGIServer, WSGIHandler
from config import SERVER_IP, SERVER_PORT, NOTIFIER_BINDINGS, MQTT_VTN_BROKER_IP, MQTT_VTN_BROKER_PORT, MQTT_BROKER_CLIENT_ID, \
    MQTT_BROKER_USERNAME, MQTT_BROKER_PASSWORD, MQTT_BROKER_AUTH, \
    MDNS_ENABLED, MDNS_SERVICE_NAME, OIDC_AUTH_ENABLED


class CloseConnectionHandler(WSGIHandler):
    """Force Connection: close on every response to prevent keep-alive connection accumulation."""
    close_connection = True


def _regenerate_ven_credentials():
    """On startup, regenerate MQTT credentials for all existing VENs in the object store."""
    from swagger_server.objStore.storageInterface import objStore
    try:
        vens = objStore.search_all("VEN")
        if isinstance(vens, list):
            for ven in vens:
                ven_id = getattr(ven, 'id', None)
                if ven_id:
                    globals.DYNSEC.regenerate_ven_credentials(ven_id)
            logging.info(f"main(), Regenerated MQTT credentials for {len(vens)} existing VEN(s)")
    except:
        logging.warning(f"main(), exception regenerating VEN credentials", exc_info=True)


def main():
    # MQTTC is a global needed by others, AFAICT this is the only way they can get it...

    if ('MQTT' in NOTIFIER_BINDINGS) and MQTT_VTN_BROKER_IP and MQTT_VTN_BROKER_PORT:
        # Instantiate MqttClient
        try:
            globals.MQTTC = mqtt.MqttClient(client_id=MQTT_BROKER_CLIENT_ID,
                                            endpoint=MQTT_VTN_BROKER_IP,
                                            port=MQTT_VTN_BROKER_PORT,
                                            username=MQTT_BROKER_USERNAME,
                                            password=MQTT_BROKER_PASSWORD)
            globals.MQTTC.start()
            logging.info(f"main(), Instantiated MqttClient, client_id={MQTT_BROKER_CLIENT_ID}, endpoint={MQTT_VTN_BROKER_IP}, port={MQTT_VTN_BROKER_PORT}")

            # Initialize dynsec manager if broker auth is configured
            if MQTT_BROKER_AUTH != 'ANONYMOUS' and MQTT_BROKER_USERNAME:
                try:
                    import gevent
                    gevent.sleep(1)  # Allow MQTT connection to establish
                    globals.DYNSEC = dynsec.DynsecManager(globals.MQTTC)
                    logging.info(f"main(), Initialized DynsecManager")
                    # Regenerate MQTT credentials for all existing VENs
                    _regenerate_ven_credentials()
                except:
                    logging.warning(f"main(), exception initializing DynsecManager", exc_info=True)
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
    if MDNS_ENABLED:
        # Auth is always required (basic or OIDC)
        mdns.start(SERVER_IP, SERVER_PORT, MDNS_SERVICE_NAME, requires_auth=True)

    http_server = WSGIServer((SERVER_IP, SERVER_PORT), app, handler_class=CloseConnectionHandler)
    try:
        http_server.serve_forever()
    finally:
        if MDNS_ENABLED:
            mdns.stop()


if __name__ == '__main__':
    main()
