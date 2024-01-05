# coding: utf-8

from __future__ import absolute_import

from flask import json

from swagger_server.models.program import Program  # noqa: E501
from swagger_server.test import BaseTestCase

BASE_URL = 'http://localhost:8080/openadr3/3.0.1'
auth_header = {'Authorization': 'Bearer bl_token'}


class TestProgramsController(BaseTestCase):
    """ProgramsController integration test stubs"""

    def test_create_program(self):
        """Test case for create_program

        create a program
        """
        body = Program(program_name='myProgram')
        response = self.client.open(
            BASE_URL + 'programs',
            method='POST',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_all_programs(self):
        """Test case for search_all_programs

        searches all programs
        """
        response = self.client.get(
            BASE_URL + 'programs',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_program_by_program_id(self):
        """Test case for search_program_by_program_id

        searches programs by program ID
        """
        response = self.client.open(
            BASE_URL + 'programs/0',
            method='GET',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_program(self):
        """Test case for update_program

        update a program
        """
        body = Program(program_name="myProgram")
        response = self.client.open(
            BASE_URL + 'programs/0',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    # Tests run in alphabetical order, so put this last so search_by_id and update work on id=0
    def test_xdelete_program(self):
        """Test case for delete_program

        delete a program
        """
        response = self.client.open(
            BASE_URL + 'programs/0',
            method='DELETE',
            headers=auth_header)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
