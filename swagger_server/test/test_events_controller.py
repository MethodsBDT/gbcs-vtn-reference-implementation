# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.event import Event  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.test import BaseTestCase

BASE_URL = 'http://localhost:8080/openadr3/OADR-3.0.0/1.0.0/'
auth_header = {'Authorization': "Bearer bl_token"}

class TestEventsController(BaseTestCase):
    """EventsController integration test stubs"""

    def test_create_event(self):
        """Test case for create_event

        create an event
        """
        body = Event(program_id="0", intervals=[])
        response = self.client.open(
            BASE_URL+'events',
            method='POST',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    # Tests run in alphabetical order, so put this last so search_by_id and update work on id=0
    def test_xdelete_event(self):
        """Test case for delete_event

        delete an event
        """
        response = self.client.open(
            BASE_URL+'events/0',
            method='DELETE',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_all_events(self):
        """Test case for search_all_events

        searches all events
        """
        response = self.client.open(
            BASE_URL+'events',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_events_by_id(self):
        """Test case for search_events_by_id

        search events by ID
        """
        response = self.client.open(
            BASE_URL+'events/0',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_event(self):
        """Test case for update_event

        update an event
        """
        body = Event(program_id="0", intervals=[])
        response = self.client.open(
            BASE_URL+'events/0',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
