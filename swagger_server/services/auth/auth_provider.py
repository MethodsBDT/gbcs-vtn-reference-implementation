from connexion.exceptions import ProblemException

from config import OIDC_AUTH_ENABLED
from swagger_server.services.auth.auth_exception import AuthException
from swagger_server.services.auth.oadr_auth_provider import OadrAuthProvider
from swagger_server.services.auth.oadr_auth_provider_basic import BasicAuthProvider
from swagger_server.services.auth.oadr_auth_provider_oidc import OIDCAuthProvider

class AuthServiceProvider:
    def __init__(self):
        self.auth_provider: OadrAuthProvider = OIDCAuthProvider() if OIDC_AUTH_ENABLED else BasicAuthProvider()

    def get_token(self, client_id: str, secret_id: str) -> str:
        try:
            return self.auth_provider.get_token(client_id, secret_id)
        except AuthException as e:
            raise ProblemException(status=403, title='Forbidden', detail=e.description)

    def get_scopes(self, token: str) -> list[str]:
        if self.auth_provider.validate_token(token):
            return self.auth_provider.get_scope(token)
        else:
            raise ProblemException(status=403, title='Forbidden', detail='Provided token is invalid')
