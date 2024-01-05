# coding: utf-8

from __future__ import absolute_import

from flask import json

from swagger_server.models.subscription import Subscription  # noqa: E501
from swagger_server.test import BaseTestCase

BASE_URL = 'http://localhost:8080/openadr3/3.0.1'
auth_header = {'Authorization': 'Bearer ven_token'}


class TestSubscriptionsController(BaseTestCase):
    """SubscriptionsController integration test stubs"""

    def test_create_subscription(self):
        """Test case for create_subscription

        create subscription
        """
        body = Subscription(client_name="myClient", object_operations=[], program_id="0")
        response = self.client.open(
            BASE_URL + 'subscriptions',
            method='POST',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    # Tests run in alphabetical order, so put this last so search_by_id and update work on id=0
    def test_xdelete_subscription(self):
        """Test case for delete_subscription

        delete  subscription
        """
        response = self.client.open(
            BASE_URL + 'subscriptions/0',
            method='DELETE',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_subscription_by_id(self):
        """Test case for search_subscription_by_id

        search subscriptions by ID
        """
        response = self.client.open(
            BASE_URL + 'subscriptions/0',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_subscriptions(self):
        """Test case for search_subscriptions

        search subscriptions
        """
        response = self.client.open(
            BASE_URL + 'subscriptions',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_subscription(self):
        """Test case for update_subscription

        update  subscription
        """
        body = Subscription(client_name="myClient", object_operations=[], program_id="0")
        response = self.client.open(
            BASE_URL + 'subscriptions/0',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
