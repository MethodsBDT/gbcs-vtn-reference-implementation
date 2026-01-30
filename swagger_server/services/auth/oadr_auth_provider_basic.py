import base64
from typing import Any

from swagger_server.services.auth.auth_exception import AuthException
from swagger_server.services.auth.oadr_auth_provider import OadrAuthProvider

from config import AUTH_BASIC_VEN_CLIENT_ID, AUTH_BASIC_VEN_SECRET, AUTH_BASIC_BL_CLIENT_ID, AUTH_BASIC_BL_SECRET

def decode_basic(token: str) -> tuple[str, str] | None:
    try:
        padded = token + '=' * (-len(token) % 4)
        decoded_bytes = base64.b64decode(padded, validate=True)
        decoded_str = decoded_bytes.decode('utf-8')

        if ':' not in decoded_str:
            return None

        client_id, client_secret = decoded_str.split(':', 1)
        return client_id, client_secret

    except (base64.binascii.Error, UnicodeDecodeError):
        return None  # not valid Base64 or not UTF-8 decodable

class BasicAuthProvider(OadrAuthProvider):

    def get_token(self, client_id: str, client_secret: str) -> str:
        message = client_id + ':' + client_secret
        message_bytes = message.encode()
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode()
        return base64_message

    def validate_token(self, token: str) -> bool:
        result = decode_basic(token)
        if result is None:
            return False
        client_id, client_secret = result
        if client_id == AUTH_BASIC_VEN_CLIENT_ID and client_secret == AUTH_BASIC_VEN_SECRET:
            return True
        if client_id == AUTH_BASIC_BL_CLIENT_ID and client_secret == AUTH_BASIC_BL_SECRET:
            return True
        return False

    def get_scope(self, token: str) -> list[str]:
        result = decode_basic(token)
        if result is None:
            raise AuthException('Provided credentials are invalid')
        client_id, client_secret = result
        if client_id == AUTH_BASIC_VEN_CLIENT_ID and client_secret == AUTH_BASIC_VEN_SECRET:
            return ['test/VEN']
        if client_id == AUTH_BASIC_BL_CLIENT_ID and client_secret == AUTH_BASIC_BL_SECRET:
            return ['test/BL']
        raise AuthException('Provided credentials are invalid')

    def get_client_id(self, token: str) -> Any | None:
        if  self.validate_token(token):
            client_id, _ = decode_basic(token)
            return client_id
        return None


