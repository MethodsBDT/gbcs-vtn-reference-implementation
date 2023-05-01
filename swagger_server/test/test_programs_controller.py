# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.program import Program  # noqa: E501
from swagger_server.test import BaseTestCase


class TestProgramsController(BaseTestCase):
    """ProgramsController integration test stubs"""

    def test_create_program(self):
        """Test case for create_program

        create a program
        """
        body = Program()
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/programs',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_program(self):
        """Test case for delete_program

        delete a program
        """
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/programs/{programID}'.format(program_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_all_programs(self):
        """Test case for search_all_programs

        searches all programs
        """
        query_string = [('no_defaults', true),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/programs',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_program_by_program_id(self):
        """Test case for search_program_by_program_id

        searches programs by program ID
        """
        query_string = [('no_defaults', true)]
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/programs/{programID}'.format(program_id=56),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_program(self):
        """Test case for update_program

        update a program
        """
        body = Program()
        response = self.client.open(
            '/francisrsandoval/OpenADR-3.0/1.0.0/programs/{programID}'.format(program_id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
