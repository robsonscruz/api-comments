import unittest
from api import app

class BaseCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()