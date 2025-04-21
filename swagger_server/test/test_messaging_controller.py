# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.brokers_response import BrokersResponse  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.test import BaseTestCase


class TestMessagingController(BaseTestCase):
    """MessagingController integration test stubs"""

    def test_list_all_brokers(self):
        """Test case for list_all_brokers

        List all message broker bindings
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
