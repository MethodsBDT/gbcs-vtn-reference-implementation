import logging

from config import OIDC_BASE_URL
from config import OIDC_KNOWN_ISSUER
import requests
import jwt
from jwt.exceptions import PyJWTError

from swagger_server.services.auth.AuthException import AuthException


class OIDCAuthProvider:
    def __init__(self):
        self.base_url = OIDC_BASE_URL
        self.know_issuer_client = jwt.PyJWKClient(OIDC_KNOWN_ISSUER + '/.well-known/jwks.json')

    def get_token(self, client_id: str, client_secret: str) -> str:
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        http_response = requests.post(self.base_url + '/oauth2/token', data=payload)
        if http_response.status_code != 200:
            logging.debug(f'Failed to fetch token: {http_response.content}')
            raise AuthException('Provided credentials are invalid')
        response_json = http_response.json()
        return response_json['access_token']

    def validate_token(self, token: str) -> bool:
        try:
            public_keys = self.know_issuer_client.get_signing_keys(refresh=False)
            token_headers = jwt.get_unverified_header(token)
            for key in public_keys:
                if key.key_id == token_headers['kid']:
                    jwt.decode(token, key.key, algorithms=token_headers['alg'])
                    return True
        except PyJWTError:
            return False
        return False

    def get_scope(self, token: str) -> list[str]:
        claims = jwt.decode(token, options={'verify_signature': False})
        return claims['scope'].split()
