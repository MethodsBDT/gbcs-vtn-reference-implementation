import os
import logging
import sys

# Server configuration
SERVER_PORT = 8080
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# OIDC Authorization Provider
OIDC_AUTH_ENABLED = os.getenv('OIDC_AUTH_ENABLED', False)
OIDC_BASE_URL = os.getenv('OIDC_BASE_URL', 'https://test-tool.auth.us-east-1.amazoncognito.com')
OIDC_KNOWN_ISSUER = os.getenv('OIDC_KNOWN_ISSUER', 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_N5wIYtzuO')

# Storage Implementation
STORAGE_IMPLEMENTATION = os.getenv('STORAGE_IMPLEMENTATION', 'IN_MEMORY')  # Values: IN_MEMORY, IN_FILE_TMP
