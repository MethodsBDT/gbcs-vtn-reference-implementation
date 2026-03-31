import logging
from swagger_server.services.auth.auth_provider import AuthServiceProvider

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""

auth_provider = AuthServiceProvider()
scopes = {
    'test/VEN': ['read_all', 'read_ven_objects', 'read_targets', 'write_reports', 'write_subscriptions', 'write_vens'],
    'test/BL': ['bl_scope', 'read_all', 'read_bl', 'read_ven_objects', 'read_targets', 'write_programs', 'write_events', 'write_subscriptions', 'write_vens'],
    'certification/VEN': ['read_all', 'read_ven_objects', 'read_targets', 'write_reports', 'write_subscriptions', 'write_vens'],
    'certification/BL': ['bl_scope', 'read_all', 'read_bl', 'read_ven_objects', 'read_targets', 'write_programs', 'write_events', 'write_subscriptions', 'write_vens']
}


def check_oAuth2ClientCredentials(token):
    logging.debug(f'check_oAuth2ClientCredentials: token={token}')

    external_token_scope = auth_provider.get_scopes(token)

    allowed_scopes = {'scopes': []}
    for scope in scopes:
        if scope in external_token_scope:
            allowed_scopes['scopes'].extend(scopes[scope])
    return allowed_scopes


def validate_scope_oAuth2ClientCredentials(required_scopes, token_scopes):
    logging.debug(
        f'validate_scope_oAuth2ClientCredentials: required_scopes={required_scopes} token_scopes={token_scopes}')
    return set(required_scopes).issubset(set(token_scopes))


def check_bearerAuth(token):
    logging.debug(f'check_bearerAuth: token={token}')
    return {}
