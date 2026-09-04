#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from io import BytesIO
import unittest
from unittest.mock import patch

import requests

from agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader import WebPdfReader


class NonOkResponse:
    status_code = 404

    def __init__(self):
        self.headers = {}
        self.closed = False

    def raise_for_status(self):
        message = "404 Client Error"
        raise requests.HTTPError(message, response=self)

    def close(self):
        self.closed = True


class OkResponse:
    def __init__(self, chunks, content_length=None):
        self.chunks = chunks
        self.headers = {}
        if content_length is not None:
            self.headers["Content-Length"] = content_length
        self.closed = False
        self.iterated = False

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        self.iterated = True
        yield from self.chunks

    def close(self):
        self.closed = True


class TestWebPdfReader(unittest.TestCase):
    def test_non_ok_response_surfaces_fetch_error(self):
        reader = WebPdfReader()
        url = "https://example.com/missing.pdf"
        response = NonOkResponse()

        with (
            patch(
                "agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get", return_value=response
            ) as mock_get,
            self.assertRaises(RuntimeError) as context,
        ):
            reader._load_data(url)

        self.assertIn(url, str(context.exception))
        self.assertIn("HTTP 404", str(context.exception))
        self.assertTrue(response.closed)
        mock_get.assert_called_once_with(url, timeout=20, stream=True)

    def test_declared_oversized_pdf_is_rejected_before_download(self):
        reader = WebPdfReader(max_file_size=5)
        url = "https://example.com/large.pdf"
        response = OkResponse([], content_length="6")

        with (
            patch(
                "agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get", return_value=response
            ),
            self.assertRaisesRegex(ValueError, "exceeds max_file_size"),
        ):
            reader._load_data(url)

        self.assertFalse(response.iterated)
        self.assertTrue(response.closed)

    def test_streamed_oversized_pdf_is_rejected_without_content_length(self):
        reader = WebPdfReader(max_file_size=5, stream_chunk_size=3)
        url = "https://example.com/chunked.pdf"
        response = OkResponse([b"abc", b"def"])

        with (
            patch(
                "agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get", return_value=response
            ),
            self.assertRaisesRegex(ValueError, "exceeds max_file_size"),
        ):
            reader._load_data(url)

        self.assertTrue(response.iterated)
        self.assertTrue(response.closed)

    def test_download_accepts_content_at_exact_limit(self):
        reader = WebPdfReader(max_file_size=5, stream_chunk_size=3)
        url = "https://example.com/file.pdf"
        response = OkResponse([b"ab", b"", b"cde"], content_length="5")

        with patch(
            "agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get",
            return_value=response,
        ):
            pdf_memory_file = reader._download_pdf(url)

        self.assertEqual(pdf_memory_file.read(), b"abcde")
        self.assertTrue(response.closed)

    def test_invalid_size_limits_are_rejected_before_request(self):
        reader = WebPdfReader(max_file_size=0)

        with (
            patch("agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader.requests.get") as mock_get,
            self.assertRaisesRegex(ValueError, "max_file_size"),
        ):
            reader._load_data("https://example.com/file.pdf")

        mock_get.assert_not_called()

    def test_load_data_closes_download_buffer_after_parsing(self):
        reader = WebPdfReader()
        pdf_memory_file = BytesIO(b"pdf")
        url = "https://example.com/file.pdf"

        def write_text(_input_file, output_string, **_kwargs):
            output_string.write(b"parsed text")

        with (
            patch.object(reader, "_download_pdf", return_value=pdf_memory_file),
            patch("pdfminer.high_level.extract_text_to_fp", side_effect=write_text),
        ):
            documents = reader._load_data(url)

        self.assertEqual(["parsed text"], [document.text for document in documents])
        self.assertTrue(pdf_memory_file.closed)

    def test_load_data_closes_download_buffer_when_parsing_fails(self):
        reader = WebPdfReader()
        pdf_memory_file = BytesIO(b"pdf")

        with (
            patch.object(reader, "_download_pdf", return_value=pdf_memory_file),
            patch(
                "pdfminer.high_level.extract_text_to_fp",
                side_effect=ValueError("malformed PDF"),
            ),
            self.assertRaisesRegex(ValueError, "malformed PDF"),
        ):
            reader._load_data("https://example.com/malformed.pdf")

        self.assertTrue(pdf_memory_file.closed)


if __name__ == "__main__":
    unittest.main()
