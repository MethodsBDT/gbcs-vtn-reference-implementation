# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.subscription import Subscription  # noqa: E501
from swagger_server.test import BaseTestCase


class TestSubscriptionsController(BaseTestCase):
    """SubscriptionsController integration test stubs"""

    def test_create_subscription(self):
        """Test case for create_subscription

        create subscription
        """
        body = Subscription()
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/subscriptions',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_subscription(self):
        """Test case for delete_subscription

        delete  subscription
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/subscriptions/{subscriptionID}'.format(subscription_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_subscription_by_id(self):
        """Test case for search_subscription_by_id

        search subscriptions by ID
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/subscriptions/{subscriptionID}'.format(subscription_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_subscriptions(self):
        """Test case for search_subscriptions

        search subscriptions
        """
        query_string = [('program_id', 56),
                        ('client_id', 56),
                        ('resource_types', 'resource_types_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/subscriptions',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_subscription(self):
        """Test case for update_subscription

        update  subscription
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/subscriptions/{subscriptionID}'.format(subscription_id=56),
            method='PUT')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
