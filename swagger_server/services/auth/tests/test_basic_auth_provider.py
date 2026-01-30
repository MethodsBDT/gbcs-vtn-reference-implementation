from swagger_server.services.auth.oadr_auth_provider_basic import BasicAuthProvider
from config import AUTH_BASIC_VEN_CLIENT_ID, AUTH_BASIC_VEN_SECRET, AUTH_BASIC_BL_CLIENT_ID, AUTH_BASIC_BL_SECRET

provider = BasicAuthProvider()

def test_creation_of_token_when_provide_secrets():
    token = provider.get_token(client_id='client_id', client_secret='client_secret')
    assert token == 'Y2xpZW50X2lkOmNsaWVudF9zZWNyZXQ='

def test_should_return_true_when_provide_valid_secrets():
    ven_token = provider.get_token(client_id=AUTH_BASIC_VEN_CLIENT_ID, client_secret=AUTH_BASIC_VEN_SECRET)
    bl_token = provider.get_token(client_id=AUTH_BASIC_BL_CLIENT_ID, client_secret=AUTH_BASIC_BL_SECRET)
    assert provider.validate_token(ven_token) == True
    assert provider.validate_token(bl_token) == True

def test_should_return_false_when_provide_invalid_secrets():
    ven_token = provider.get_token(client_id='not_know', client_secret='client_secret')
    bl_token = provider.get_token(client_id='bl_client', client_secret='invalid_client_secret')
    assert provider.validate_token(ven_token) == False
    assert provider.validate_token(bl_token) == False

def test_should_return_ven_scopes_when_provide_ven_token():
    ven_token = provider.get_token(client_id=AUTH_BASIC_VEN_CLIENT_ID, client_secret=AUTH_BASIC_VEN_SECRET)
    assert provider.get_scope(ven_token) == ['test/VEN']

def test_should_return_bl_scopes_when_provide_bl_token():
    bl_token = provider.get_token(client_id=AUTH_BASIC_BL_CLIENT_ID, client_secret=AUTH_BASIC_BL_SECRET)
    assert provider.get_scope(bl_token) == ['test/BL']

def test_should_return_ven_client_id_when_provide_ven_token():
    ven_token = provider.get_token(client_id=AUTH_BASIC_VEN_CLIENT_ID, client_secret=AUTH_BASIC_VEN_SECRET)
    assert provider.get_client_id(ven_token) == 'ven_client'

def test_should_not_throw_exception_for_not_basic_token():
    assert provider.validate_token('bad_token') == False