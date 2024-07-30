import connexion
from http import HTTPStatus
import logging
import six

from swagger_server.models.auth_error import AuthError  # noqa: E501
from swagger_server.models.client_credential_response import ClientCredentialResponse  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server import util
from swagger_server.services.auth.auth_provider import AuthServiceProvider


def fetch_token(**kwargs):  # noqa: E501
    """fetch a token

    Return an access token based on clientID and clientSecret. # noqa: E501

    :param grant_type: 
    :type grant_type: str
    :param client_id: 
    :type client_id: str
    :param client_secret: 
    :type client_secret: str
    :param scope: 
    :type scope: str

    :rtype: ClientCredentialResponse
    """

    body = kwargs.get('body')
    client_id = body.get('client_id')
    client_secret = body.get('client_secret')
    logging.debug(f'fetch_token: body={client_id} client_secret={client_secret}')

    auth_provider = AuthServiceProvider()
    try:
        token =  auth_provider.get_token(client_id, client_secret)
        response = ClientCredentialResponse(access_token=token, token_type="Bearer")
        return response, HTTPStatus.OK
    except IOError:
        problem = Problem(title="Could not fetch token", status=str(HTTPStatus.INTERNAL_SERVER_ERROR))
        logging.warning(f"fetch_token(): problem={problem}")
        return problem, HTTPStatus.INTERNAL_SERVER_ERROR
