# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.test import BaseTestCase


class TestVensController(BaseTestCase):
    """VensController integration test stubs"""

    def test_create_resource(self):
        """Test case for create_resource

        create resource
        """
        body = Resource()
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}/resources'.format(ven_id=56),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_ven(self):
        """Test case for create_ven

        create ven
        """
        body = Ven()
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens',
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
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}'.format(ven_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_ven_resource(self):
        """Test case for delete_ven_resource

        delete  ven resource
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}/resources/{resourceID}'.format(ven_id=56, resource_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_by_id(self):
        """Test case for search_ven_by_id

        search vens by ID
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}'.format(ven_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_resource_by_id(self):
        """Test case for search_ven_resource_by_id

        search ven resources by ID
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}/resources/{resourceID}'.format(ven_id=56, resource_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_resources(self):
        """Test case for search_ven_resources

        search ven resources
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}/resources'.format(ven_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_vens(self):
        """Test case for search_vens

        search vens
        """
        query_string = [('skip', 1),
                        ('limit', 50)]
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ven(self):
        """Test case for update_ven

        update  ven
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}'.format(ven_id=56),
            method='PUT')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ven_resource(self):
        """Test case for update_ven_resource

        update  ven resource
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/vens/{venID}/resources/{resourceID}'.format(ven_id=56, resource_id=56),
            method='PUT')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
