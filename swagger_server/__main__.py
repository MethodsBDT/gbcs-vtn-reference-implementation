#!/usr/bin/env python3

import connexion

from swagger_server import encoder
from config import SERVER_PORT

def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)
    app.run(port=SERVER_PORT)


if __name__ == '__main__':
    main()
