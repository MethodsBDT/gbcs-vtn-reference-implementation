import logging

import awsgi
import connexion
from swagger_server import encoder

app = connexion.App(__name__, specification_dir='swagger_server/swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)


def handler(event, context):
    logging.info(event)
    print(event)
    event['httpMethod'] = event['requestContext']['http']['method']
    event['path'] = event['requestContext']['http']['path']
    print(f"httpMethod: {event['httpMethod']}, path: {event['path']}, "
          f"queryStringParameters: {event['queryStringParameters']}")
    return awsgi.response(app, event, context)
