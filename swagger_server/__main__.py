#!/usr/bin/env python3

import connexion

from swagger_server import encoder
from gevent.pywsgi import WSGIServer
from config import SERVER_PORT


def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)
    http_server = WSGIServer(('0.0.0.0', SERVER_PORT), app)
    http_server.serve_forever()

if __name__ == '__main__':
    main()