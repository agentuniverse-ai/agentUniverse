#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

import requests

from agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader import WebPdfReader


class NonOkResponse:
    status_code = 404
    content = b''

    def raise_for_status(self):
        raise requests.HTTPError("404 Client Error", response=self)


class TestWebPdfReader(unittest.TestCase):
    def test_non_ok_response_surfaces_fetch_error(self):
        reader = WebPdfReader()
        url = 'https://example.com/missing.pdf'

        with patch(
            'agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get',
            return_value=NonOkResponse()
        ) as mock_get:
            with self.assertRaises(RuntimeError) as context:
                reader._load_data(url)

        self.assertIn(url, str(context.exception))
        self.assertIn('HTTP 404', str(context.exception))
        mock_get.assert_called_once_with(url, timeout=20)


if __name__ == '__main__':
    unittest.main()
