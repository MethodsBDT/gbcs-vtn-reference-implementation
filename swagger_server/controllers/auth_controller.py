import connexion
from http import HTTPStatus
import logging
import six

from swagger_server.models.client_credential_request import ClientCredentialRequest  # noqa: E501
from swagger_server.models.client_credential_response import ClientCredentialResponse  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server import util
from swagger_server.services.auth.auth_provider import AuthServiceProvider


def fetch_token(body):  # noqa: E501
    """fetch a token

    Return an access token based on clientID and clientSecret. # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: ClientCredentialResponse
    """
    if connexion.request.is_json:
        body = ClientCredentialRequest.from_dict(connexion.request.get_json())  # noqa: E501

    client_id = body.client_id
    client_secret = body.client_secret
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
