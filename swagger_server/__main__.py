#!/usr/bin/env python3

import argparse
import connexion
import logging
import os

from swagger_server import encoder

LOG_PATH='./logs'

def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-l", "--loglevel", help="log level")
    args = argParser.parse_args()

    numeric_level = logging.INFO
    if args.loglevel is not None:
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)

    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
    logging.basicConfig(filename=LOG_PATH+'/VTN.log', filemode='w', level=numeric_level)
    print ("VTN: find logs here ./logs/VTN.log")

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)
    app.run(port=8080)


if __name__ == '__main__':
    main()
