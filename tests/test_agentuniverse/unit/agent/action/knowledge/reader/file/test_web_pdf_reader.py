#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

import requests

from agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader import WebPdfReader


class NonOkResponse:
    status_code = 404
    headers = {}

    def raise_for_status(self):
        raise requests.HTTPError("404 Client Error", response=self)

    def close(self):
        pass


class StreamingResponse:
    def __init__(self, chunks, content_length=None):
        self.chunks = chunks
        self.headers = {}
        if content_length is not None:
            self.headers['Content-Length'] = str(content_length)
        self.closed = False
        self.iterated = False

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size):
        self.iterated = True
        yield from self.chunks

    def close(self):
        self.closed = True


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
        mock_get.assert_called_once_with(url, timeout=20, stream=True)

    def test_declared_oversized_pdf_is_rejected_before_download(self):
        reader = WebPdfReader()
        url = 'https://example.com/large.pdf'
        response = StreamingResponse([], reader.MAX_PDF_SIZE_BYTES + 1)

        with patch(
            'agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get',
            return_value=response
        ):
            with self.assertRaisesRegex(RuntimeError, 'maximum download size'):
                reader._download_pdf(url)

        self.assertFalse(response.iterated)
        self.assertTrue(response.closed)

    def test_streamed_pdf_is_rejected_when_actual_size_exceeds_limit(self):
        reader = WebPdfReader()
        url = 'https://example.com/chunked.pdf'
        response = StreamingResponse([b'abc', b'def'])

        with patch.object(WebPdfReader, 'MAX_PDF_SIZE_BYTES', 5), patch(
            'agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get',
            return_value=response
        ):
            with self.assertRaisesRegex(RuntimeError, 'maximum download size'):
                reader._download_pdf(url)

        self.assertTrue(response.closed)

    def test_pdf_within_limit_is_returned(self):
        reader = WebPdfReader()
        url = 'https://example.com/small.pdf'
        response = StreamingResponse([b'%PDF', b'-test'], content_length=9)

        with patch(
            'agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get',
            return_value=response
        ):
            pdf_memory_file = reader._download_pdf(url)

        self.assertEqual(pdf_memory_file.read(), b'%PDF-test')
        self.assertTrue(response.closed)


if __name__ == '__main__':
    unittest.main()
