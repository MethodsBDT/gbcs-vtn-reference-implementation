# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.client_credential_response import ClientCredentialResponse  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAuthController(BaseTestCase):
    """AuthController integration test stubs"""

    def test_fetch_token(self):
        """Test case for fetch_token

        fetch a token
        """
        data = dict(grant_type='grant_type_example',
                    client_id='client_id_example',
                    client_secret='client_secret_example',
                    scope='scope_example')
        response = self.client.open(
            '/openadr3/3.1.0/auth/token',
            method='POST',
            data=data,
            content_type='application/x-www-form-urlencoded')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
