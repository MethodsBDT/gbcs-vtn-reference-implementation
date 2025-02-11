import connexion

from swagger_server import encoder
from gevent.pywsgi import WSGIServer
from config import SERVER_PORT


def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', base_path="/openadr3/3.1.0", arguments={'title': 'OpenADR REST Demand Response API'}, pythonic_params=True)
    # Note that the OpenADR3 protocol can run on any path; we're choosing to run it
    # on /openadr3/3.1.0.
    http_server = WSGIServer(('0.0.0.0', SERVER_PORT), app)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
