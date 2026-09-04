# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @Email   : ai-assistant@example.com
# @FileName: test_custom_flask_request_sink.py

"""Unit tests for CustomFlaskRequestSink.generate_log."""

import unittest

from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.utils.log_sink.custom_flask_request_sink import \
    CustomFlaskRequestSink


class FakeFlaskRequest(object):
    """Minimal fake of a flask request exposing the attributes used by the sink."""

    def __init__(self, method='GET', path='/', headers=None, data=b''):
        self.method = method
        self.path = path
        self.headers = headers if headers is not None else {}
        self.data = data

    def get_data(self, as_text=False):
        return self.data.decode('utf-8') if as_text else self.data


class CustomFlaskRequestSinkTest(unittest.TestCase):
    """Unit tests for CustomFlaskRequestSink."""

    def setUp(self):
        """Set up the sink instance under test."""
        self.sink = CustomFlaskRequestSink()

    def test_generate_log_contains_method_and_path(self):
        request = FakeFlaskRequest(method='POST', path='/api/search')
        log = self.sink.generate_log(request)
        self.assertIn('Request: POST /api/search', log)

    def test_generate_log_contains_request_headers(self):
        request = FakeFlaskRequest(headers={'X-Token': 'abc123'})
        log = self.sink.generate_log(request)
        self.assertIn("Headers: {'X-Token': 'abc123'}", log)

    def test_generate_log_contains_plain_body_when_present(self):
        request = FakeFlaskRequest(method='POST', data=b'payload-data')
        log = self.sink.generate_log(request)
        self.assertTrue(log.endswith(' Body: payload-data'))

    def test_generate_log_omits_body_when_data_is_empty(self):
        request = FakeFlaskRequest(method='GET', data=b'')
        log = self.sink.generate_log(request)
        self.assertNotIn('Body:', log)

    def test_generate_log_swallows_body_read_errors(self):
        request = FakeFlaskRequest(method='POST', data=b'boom')

        def broken_get_data(as_text=False):
            raise ValueError('cannot read body')

        request.get_data = broken_get_data
        log = self.sink.generate_log(request)
        self.assertNotIn('Body:', log)
        self.assertIn('Request: POST /', log)

    def test_generate_log_returns_string(self):
        request = FakeFlaskRequest(method='GET', path='/health')
        self.assertIsInstance(self.sink.generate_log(request), str)


if __name__ == '__main__':
    unittest.main()
