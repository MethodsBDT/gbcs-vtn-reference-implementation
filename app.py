import logging
import sys

import awsgi
from flask import Flask
# import connexion
# from swagger_server import encoder

# app = connexion.App(__name__, specification_dir='swagger_server/swagger/')
# app.app.json_encoder = encoder.JSONEncoder
# app.add_api('swagger.yaml', arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/world")
def hello2():
    return "Hello, test different route!"


def handler(event, context):
    logging.info(event)
    return awsgi.response(app, event, context)
