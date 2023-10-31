import logging
from swagger_server.services.auth.auth_provider import AuthServiceProvider

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""

auth_provider = AuthServiceProvider()
VEN_SCOPES = ['read_all', 'write_reports', 'write_subscriptions', 'write_vens']
BL_SCOPES = ['read_all', 'write_programs', 'write_events', 'write_subscriptions', 'write_vens']


def check_oAuth2ClientCredentials(token):
    logging.debug(f"check_oAuth2ClientCredentials: token={token}")

    external_token_scope = auth_provider.get_scopes(token)

    allowed_scopes = {'scopes': []}
    if 'test-tool/TEST_VEN' in external_token_scope:
        allowed_scopes['scopes'].extend(VEN_SCOPES)
    if 'test-tool/TEST_BL' in external_token_scope:
        allowed_scopes['scopes'].extend(BL_SCOPES)
    return allowed_scopes


def validate_scope_oAuth2ClientCredentials(required_scopes, token_scopes):
    logging.debug(
        f"validate_scope_oAuth2ClientCredentials: required_scopes={required_scopes} token_scopes={token_scopes}")
    return set(required_scopes).issubset(set(token_scopes))


def check_bearerAuth(token):
    logging.debug(f"check_bearerAuth: token={token}")
    return {}
    # return {'test_key': 'test_value'}
