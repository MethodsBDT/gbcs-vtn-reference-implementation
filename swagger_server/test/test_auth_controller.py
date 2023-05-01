# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAuthController(BaseTestCase):
    """AuthController integration test stubs"""

    def test_fetch_token(self):
        """Test case for fetch_token

        fetch a token
        """
        headers = [('client_id', 'client_id_example'),
                   ('client_secret', 56)]
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/auth/token',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
