import logging

from swagger_server.services.auth.AuthException import AuthException


class AuthorityModel:
    def __init__(self, client_id: str, client_secret: str, scope: list[str], token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.token = token


class MockAuthProvider:

    def __init__(self):
        self.allowed_authorities = [
            #// todo: REPLACE TOKEN VALUES
            AuthorityModel('ven_client', '999', ['test/VEN'], 'ven_token'),
            AuthorityModel('ven_client2', '9999', ['test/VEN'], 'ven_token2'),
            AuthorityModel('bl_client', '1001', ['test/BL'], 'bl_token'),
            AuthorityModel('admin_client', '1000', ['test/VEN', 'test/BL'], 'admin_token')
        ]

    def get_token(self, client_id: str, client_secret: str) -> str:
        for authority in self.allowed_authorities:
            if client_id == authority.client_id and client_secret == authority.client_secret:
                logging.debug(
                    f"fetch_token: {authority.token} client_id={authority.client_id} client_secret={authority.client_secret}")
                return authority.token
        raise AuthException('Provided credentials are invalid')

    def validate_token(self, token: str) -> bool:
        for authority in self.allowed_authorities:
            if token == authority.token:
                return True
        return False

    def get_scope(self, token: str) -> list[str]:
        for authority in self.allowed_authorities:
            if token == authority.token:
                return authority.scope
        return []

    def get_client_id(self, token: str) -> str:
        for authority in self.allowed_authorities:
            if token == authority.token:
                return authority.client_id
        return None
