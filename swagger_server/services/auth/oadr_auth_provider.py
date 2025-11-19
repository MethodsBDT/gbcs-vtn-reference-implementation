
class OadrAuthProvider:

    def get_token(self, client_id: str, client_secret: str) -> str:
        """"""
        pass

    def validate_token(self, token: str) -> bool:
        """"""
        pass

    def get_scope(self, token: str) -> list[str]:
        """"""
        pass

    def get_client_id(self, token: str) -> str:
        """"""
        pass