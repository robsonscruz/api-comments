import json

from tests.BaseCase import BaseCase

class ApiTest(BaseCase):

    def test_successful_health(self):
        # When
        response = self.app.get('/health')

        # Then
        self.assertEqual(200, response.status_code)