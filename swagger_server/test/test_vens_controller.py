# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.resource import Resource  # noqa: E501
from swagger_server.models.ven import Ven  # noqa: E501
from swagger_server.test import BaseTestCase

BASE_URL = 'http://localhost:8080/openadr3/OADR-3.0.0/1.0.0/'
auth_header = {'Authorization': "Bearer ven_token"}

class TestVensController(BaseTestCase):
    """VensController integration test stubs"""

    def test_create_resource(self):
        """Test case for create_resource

        create resource
        """
        body = Resource(resource_name="myResource")
        response = self.client.open(
            BASE_URL+'vens/0/resources',
            method='POST',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    # Tests run in alphabetical order, so put this first so create resource works on id=0
    def test_acreate_ven(self):
        """Test case for create_ven

        create ven
        """
        body = Ven(ven_name="myVen")
        response = self.client.open(
            BASE_URL+'vens',
            method='POST',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_xxdelete_ven(self):
        """Test case for delete_ven

        delete  ven
        """
        response = self.client.open(
            BASE_URL+'vens/0',
            method='DELETE',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_xdelete_ven_resource(self):
        """Test case for delete_ven_resource

        delete  ven resource
        """
        response = self.client.open(
            BASE_URL+'vens/0/resources/0',
            method='DELETE',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_by_id(self):
        """Test case for search_ven_by_id

        search vens by ID
        """
        response = self.client.open(
            BASE_URL+'vens/0',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_resource_by_id(self):
        """Test case for search_ven_resource_by_id

        search ven resources by ID
        """
        response = self.client.open(
            BASE_URL+'vens/0/resources/0',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_ven_resources(self):
        """Test case for search_ven_resources

        search ven resources
        """
        response = self.client.open(
            BASE_URL+'vens/0/resources',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_vens(self):
        """Test case for search_vens

        search vens
        """
        response = self.client.open(
            BASE_URL+'vens',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ven(self):
        """Test case for update_ven

        update  ven
        """
        body = Ven(ven_name="myVen")
        response = self.client.open(
            BASE_URL+'vens/0',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ven_resource(self):
        """Test case for update_ven_resource

        update  ven resource
        """
        body = Resource(resource_name="myResource")
        response = self.client.open(
            BASE_URL+'vens/0/resources/0',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
