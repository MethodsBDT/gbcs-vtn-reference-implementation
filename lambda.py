import logging

import awsgi
import connexion

from swagger_server import encoder

logging.getLogger().setLevel(logging.INFO)
app = connexion.App(__name__, specification_dir='swagger_server/swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml',
            base_path='/openadr3/3.1.0',
            arguments={'title': 'OpenADR REST Demand Response API'},
            pythonic_params=True)


def handler(event, context):
    # logging.info(event)
    event['httpMethod'] = event['requestContext']['http']['method']
    event['path'] = event['requestContext']['http']['path']
    event['queryStringParameters'] = event.get('queryStringParameters')
    logging.info(f"httpMethod: {event['httpMethod']}, path: {event['path']}, "
          f"queryStringParameters: {event.get('queryStringParameters')}")
    return awsgi.response(app, event, context)
