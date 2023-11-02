from connexion.exceptions import OAuthProblem, OAuthScopeProblem, ProblemException

from config import OIDC_AUTH_ENABLED
from swagger_server.services.auth.AuthException import AuthException
from swagger_server.services.auth.oidc_auth_provider import OIDCAuthProvider
from swagger_server.services.auth.mock_auth_provider import MockAuthProvider


class AuthServiceProvider:
    def __init__(self):
        self.auth_provider = OIDCAuthProvider() if OIDC_AUTH_ENABLED else MockAuthProvider()

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
