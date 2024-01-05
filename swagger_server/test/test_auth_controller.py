# coding: utf-8

from __future__ import absolute_import

from swagger_server.test import BaseTestCase

BASE_URL = 'http://localhost:8080/openadr3/3.0.1'


class TestAuthController(BaseTestCase):
    """AuthController integration test stubs"""

    def test_fetch_token(self):
        """Test case for fetch_token

        fetch a token
        """
        headers = [('clientID', 'ven_client'),
                   ('clientSecret', 999)]
        response = self.client.open(
            BASE_URL + 'auth/token',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
