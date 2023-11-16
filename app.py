import logging

import awsgi
import connexion
from swagger_server import encoder

app = connexion.App(__name__, specification_dir='swagger_server/swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/world")
def hello2():
    return "Hello, test different route!"


def handler(event, context):
    logging.info(event)
    print(event)
    event['httpMethod'] = event['requestContext']['http']['method']
    event['path'] = event['requestContext']['http']['path']
    event['queryStringParameters'] = event['rawQueryString']
    print(
        f"httpMethod: {event['httpMethod']}, path: {event['path']}, queryStringParameters: {event['queryStringParameters']}")
    return awsgi.response(app, event, context)
