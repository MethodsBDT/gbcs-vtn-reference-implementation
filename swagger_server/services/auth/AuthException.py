class AuthException(Exception):
    def __init__(self, description: str):
        self.description = description
