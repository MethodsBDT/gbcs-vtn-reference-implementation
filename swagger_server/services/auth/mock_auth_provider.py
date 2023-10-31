import logging


class AuthorityModel:
    def __init__(self, client_id: str, client_secret: str, scope: list[str], token: str, ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.token = token


class MockAuthProvider:

    def __init__(self):
        self.allowed_authorities = [
            AuthorityModel('ven_client', '999', ['test-tool/TEST_VEN'], 'ven_token'),
            AuthorityModel('bl_client', '1001', ['test-tool/TEST_BL'], 'bl_token'),
            AuthorityModel('admin_client', '1000', ['test-tool/TEST_VEN', 'test-tool/TEST_BL'], 'admin_token')
        ]

    def get_token(self, client_id: str, client_secret: str) -> str:
        for authority in self.allowed_authorities:
            if client_id == authority.client_id and client_secret == authority.client_secret:
                logging.debug(
                    f"fetch_token: {authority.token} client_id={authority.client_id} client_secret={authority.client_secret}")
                return authority.token
        return 'bad_token'  # TODO: I am not sure if in oauth2 you can generate something like bad token, replace with 403

    def validate_token(self, token: str) -> bool:
        for authority in self.allowed_authorities:
            if token == authority.token:
                return True
        return False

    def get_scope(self, token: str) -> list[str]:
        if token == 'ven_token':
            return ['test-tool/TEST_VEN']
        elif token == 'bl_token':
            return ['test-tool/TEST_BL']
        elif token == 'admin_token':
            return ['test-tool/TEST_VEN', 'test-tool/TEST_BL']
        else:
            return []
