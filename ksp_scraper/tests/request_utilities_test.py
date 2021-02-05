import unittest
import request_utilities
from unittest.mock import Mock, patch
import requests
import requests_mock


class TestRequestUtilities(unittest.TestCase):

    def setUp(self) -> None:
        self.testdata = open('test_requests.html').read()

    def test_get_text_from_url(self):
        with requests_mock.Mocker() as mocker:
            mocker.get('http://test.com', text=self.testdata)
            self.assertEqual(len(request_utilities.get_text_from_url('http://test.com')), 2)
            self.assertEqual(str(type(request_utilities.get_text_from_url('http://test.com'))),
                             "<class 'bs4.BeautifulSoup'>")
