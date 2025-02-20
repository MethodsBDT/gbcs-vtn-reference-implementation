#!/usr/bin/env python3

import connexion

from swagger_server import encoder


def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', base_path="/openadr3/3.1.0", arguments={'title': 'OpenADR 3 API'}, pythonic_params=True)
    # Note that the OpenADR3 protocol can run on any path; we're choosing to run it
    # on /openadr3/3.1.0.
    app.run(port=8080)


if __name__ == '__main__':
    main()
