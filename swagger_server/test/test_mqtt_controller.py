# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.topics_mqtt_program_events_response import TopicsMqttProgramEventsResponse  # noqa: E501
from swagger_server.models.topics_mqtt_program_reports_response import TopicsMqttProgramReportsResponse  # noqa: E501
from swagger_server.models.topics_mqtt_program_response import TopicsMqttProgramResponse  # noqa: E501
from swagger_server.models.topics_mqtt_program_subscriptions_response import TopicsMqttProgramSubscriptionsResponse  # noqa: E501
from swagger_server.models.topics_mqtt_programs_response import TopicsMqttProgramsResponse  # noqa: E501
from swagger_server.models.topics_mqtt_ven_resources_response import TopicsMqttVenResourcesResponse  # noqa: E501
from swagger_server.models.topics_mqtt_vens_response import TopicsMqttVensResponse  # noqa: E501
from swagger_server.test import BaseTestCase


class TestMqttController(BaseTestCase):
    """MqttController integration test stubs"""

    def test_list_all_mqtt_topics_program(self):
        """Test case for list_all_mqtt_topics_program

        List all MQTT binding topic names for operations on a program 
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers/mqtt/topics/programs/{programID}'.format(program_id=ObjectID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_all_mqtt_topics_program_events(self):
        """Test case for list_all_mqtt_topics_program_events

        List all MQTT binding topic names for operations on events for a program 
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers/mqtt/topics/programs/{programID}/events'.format(program_id=ObjectID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_all_mqtt_topics_program_reports(self):
        """Test case for list_all_mqtt_topics_program_reports

        List all MQTT binding topic names for operations on reports for a program 
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers/mqtt/topics/programs/{programID}/reports'.format(program_id=ObjectID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_all_mqtt_topics_program_subscriptions(self):
        """Test case for list_all_mqtt_topics_program_subscriptions

        List all MQTT binding topic names for operations on subscriptions for a program 
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers/mqtt/topics/programs/{programID}/subscriptions'.format(program_id=ObjectID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_all_mqtt_topics_programs(self):
        """Test case for list_all_mqtt_topics_programs

        List all MQTT binding topic names for operations on programs 
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers/mqtt/topics/programs',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_all_mqtt_topics_ven_resources(self):
        """Test case for list_all_mqtt_topics_ven_resources

        List all MQTT binding topic names for operations on resources for a ven 
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers/mqtt/topics/vens/{venID}/resources'.format(ven_id=ObjectID()),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_all_mqtt_topics_vens(self):
        """Test case for list_all_mqtt_topics_vens

        List all MQTT binding topic names for operations on vens 
        """
        response = self.client.open(
            '/openadr3/3.1.0/brokers/mqtt/topics/vens',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
