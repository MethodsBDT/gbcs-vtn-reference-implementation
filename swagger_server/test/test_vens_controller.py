# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.resource_request import ResourceRequest  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.models.ven_request import VenRequest  # noqa: E501
from swagger_server.test import BaseTestCase


class TestVensController(BaseTestCase):
    """VensController integration test stubs"""

    def test_create_resource(self):
        """Test case for create_resource

        create resource
        """
        body = ResourceRequest()
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}/resources'.format(ven_id=ObjectID()),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_ven(self):
        """Test case for create_ven

        create ven
        """
        body = VenRequest()
        response = self.client.open(
            '/openadr3/3.1.0/vens',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_ven(self):
        """Test case for delete_ven

        delete  ven
        """
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}'.format(ven_id=ObjectID()),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_ven_resource(self):
        """Test case for delete_ven_resource

        delete  ven resource
        """
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}/resources/{resourceID}'.format(ven_id=ObjectID(), resource_id=ObjectID()),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_by_id(self):
        """Test case for search_ven_by_id

        search vens by ID
        """
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}'.format(ven_id=ObjectID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_resource_by_id(self):
        """Test case for search_ven_resource_by_id

        search ven resources by ID
        """
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}/resources/{resourceID}'.format(ven_id=ObjectID(), resource_id=ObjectID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_resources(self):
        """Test case for search_ven_resources

        search ven resources
        """
        query_string = [('resource_name', 'resource_name_example'),
                        ('target_type', 'target_type_example'),
                        ('target_values', 'target_values_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}/resources'.format(ven_id=ObjectID()),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_vens(self):
        """Test case for search_vens

        search vens
        """
        query_string = [('ven_name', 'ven_name_example'),
                        ('target_type', 'target_type_example'),
                        ('target_values', 'target_values_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open(
            '/openadr3/3.1.0/vens',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ven(self):
        """Test case for update_ven

        update  ven
        """
        body = VenRequest()
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}'.format(ven_id=ObjectID()),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ven_resource(self):
        """Test case for update_ven_resource

        update  ven resource
        """
        body = ResourceRequest()
        response = self.client.open(
            '/openadr3/3.1.0/vens/{venID}/resources/{resourceID}'.format(ven_id=ObjectID(), resource_id=ObjectID()),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
