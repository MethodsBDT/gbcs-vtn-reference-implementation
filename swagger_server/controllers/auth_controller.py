import connexion
import logging

from swagger_server.services.auth.auth_provider import AuthServiceProvider


def fetch_token():  # noqa: E501
    """fetch a token

    Return an access token based on clientID and clientSecret. # noqa: E501

    :rtype: str
    """
    client_id = connexion.request.headers["clientID"]
    client_secret = connexion.request.headers["clientSecret"]

    logging.debug(f"fetch_token: client_id={client_id} client_secret={client_secret}")

    auth_provider = AuthServiceProvider()
    try:
        return auth_provider.get_token(client_id, client_secret)
    except IOError:
        logging.error("Could not fetch token")
