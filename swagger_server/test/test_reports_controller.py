# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.report import Report  # noqa: E501
from swagger_server.test import BaseTestCase

BASE_URL = 'http://localhost:8080/openadr3/OADR-3.0.0/1.0.0/'
auth_header = {'Authorization': "Bearer ven_token"}

class TestReportsController(BaseTestCase):
    """ReportsController integration test stubs"""

    def test_create_report(self):
        """Test case for create_report

        add a report
        """
        body = Report(client_name="myClient", event_id="0", program_id="0", resources=[])
        response = self.client.open(
            BASE_URL+'reports',
            method='POST',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    # Tests run in alphabetical order, so put this last so search_by_id and update work on id=0
    def test_xdelete_report(self):
        """Test case for delete_report

        delete a report
        """
        response = self.client.open(
            BASE_URL+'reports/0',
            method='DELETE',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_all_reports(self):
        """Test case for search_all_reports

        searches all reports
        """
        response = self.client.open(
            BASE_URL+'reports',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_reports_by_report_id(self):
        """Test case for search_reports_by_report_id

        searches reports by reportID
        """
        response = self.client.open(
            BASE_URL+'reports/0',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_report(self):
        """Test case for update_report

        update a report
        """
        body = Report(client_name="myClient", event_id="0", program_id="0", resources=[])
        response = self.client.open(
            BASE_URL+'reports/0',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
