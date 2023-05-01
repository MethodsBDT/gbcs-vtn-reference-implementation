# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.event import Event  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.test import BaseTestCase


class TestEventsController(BaseTestCase):
    """EventsController integration test stubs"""

    def test_create_event(self):
        """Test case for create_event

        create an event
        """
        body = Event()
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/events',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_event(self):
        """Test case for delete_event

        delete an event
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/events/{eventID}'.format(event_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_all_events(self):
        """Test case for search_all_events

        searches all events
        """
        query_string = [('program_id', 56),
                        ('no_defaults', true),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/events',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_events_by_id(self):
        """Test case for search_events_by_id

        search events by ID
        """
        query_string = [('no_defaults', true)]
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/events/{eventID}'.format(event_id=56),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_event(self):
        """Test case for update_event

        update an event
        """
        body = Event()
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/events/{eventID}'.format(event_id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
