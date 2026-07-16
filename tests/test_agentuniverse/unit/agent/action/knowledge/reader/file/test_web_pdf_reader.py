#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader import WebPdfReader


class TestWebPdfReader(unittest.TestCase):
    def test_non_ok_response_returns_empty_list(self):
        reader = WebPdfReader()

        with patch(
            'agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get',
            return_value=SimpleNamespace(status_code=404, content=b'')
        ):
            docs = reader._load_data('https://example.com/missing.pdf')

        self.assertEqual(docs, [])


if __name__ == '__main__':
    unittest.main()
