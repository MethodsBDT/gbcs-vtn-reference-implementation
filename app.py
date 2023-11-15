import logging

import awsgi
from flask import Flask
# import connexion
# from swagger_server import encoder

# app = connexion.App(__name__, specification_dir='swagger_server/swagger/')
# app.app.json_encoder = encoder.JSONEncoder
# app.add_api('swagger.yaml', arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/world")
def hello2():
    return "Hello, test different route!"


def handler(event, context):
    logging.debug(event)
    return awsgi.response(app, event, context)
