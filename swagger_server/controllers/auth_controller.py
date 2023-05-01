import connexion
import logging
import six

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server import util


def fetch_token(client_id, client_secret):  # noqa: E501
    """fetch a token

    Return an access token based on clientID # noqa: E501

    :param client_id: bearer token.
    :type client_id: str

    :rtype: str
    """
    logging.debug(f"fetch_token: client_id={client_id} client_secret={client_secret}")
    if client_id == 'ven_client' and client_secret == 999:
        logging.debug(f"fetch_token: ven_token client_id={client_id} client_secret={client_secret}")
        return 'ven_token'
    elif client_id == 'bl_client' and client_secret == 1001:
        logging.debug(f"fetch_token: bl_token client_id={client_id} client_secret={client_secret}")
        return 'bl_token'
    else:
        logging.debug(f"fetch_token: bad_token client_id={client_id} client_secret={client_secret}")
        return 'bad_token'


