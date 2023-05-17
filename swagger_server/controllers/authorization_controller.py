import logging
from typing import List
"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""
def check_oAuth2ClientCredentials(token):
    logging.debug(f"check_oAuth2ClientCredentials: token={token}")
    if token == 'ven_token':
        return {'scopes': ['read_all', 'write_reports', 'write_subscriptions', 'write_vens'], 'uid': 'ALL'}
    elif token == 'bl_token':
        return {'scopes': ['read_all', 'write_programs', 'write_events', 'write_reports', 'write_subscriptions', 'write_vens'], 'uid': 'ALL'}
    else:
        return {}

def validate_scope_oAuth2ClientCredentials(required_scopes, token_scopes):
    logging.debug(f"validate_scope_oAuth2ClientCredentials: required_scopes={required_scopes} token_scopes={token_scopes}")
    return set(required_scopes).issubset(set(token_scopes))


def check_bearerAuth(token):
    return {'test_key': 'test_value'}