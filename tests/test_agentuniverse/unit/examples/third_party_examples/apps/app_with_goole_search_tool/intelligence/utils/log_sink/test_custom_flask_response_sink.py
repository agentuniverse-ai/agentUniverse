# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_custom_flask_response_sink.py

"""Unit tests for the CustomFlaskResponseSink log formatter."""

import pytest

from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.utils.log_sink.custom_flask_response_sink import (
    CustomFlaskResponseSink,
)


class FakeFlaskResponse:
    """Minimal stand-in for a Flask response object."""

    def __init__(self, status_code, content_type, data, body_text):
        self.status_code = status_code
        self.content_type = content_type
        self.data = data
        self._body_text = body_text

    def get_data(self, as_text=True):
        return self._body_text if as_text else self.data


@pytest.fixture
def sink():
    return CustomFlaskResponseSink()


class TestCustomFlaskResponseSink:
    def test_generate_log_with_string_response(self, sink):
        log = sink.generate_log("plain body", 1.234)
        assert log == "Response: plain body Duration: 1.234s"

    def test_generate_log_with_response_object(self, sink):
        response = FakeFlaskResponse(200, "application/json", b'{"k": 1}', '{"k": 1}')
        log = sink.generate_log(response, 0.5)
        assert "Response: 200 application/json" in log
        assert "Duration: 0.500s" in log
        assert 'Data:{"k": 1}' in log

    def test_generate_log_without_data_appends_no_data(self, sink):
        response = FakeFlaskResponse(404, "text/html", b"", "")
        log = sink.generate_log(response, 0.25)
        assert log == "Response: 404 text/html Duration: 0.250s"
        assert "Data:" not in log

    def test_generate_log_formats_elapsed_time(self, sink):
        response = FakeFlaskResponse(200, "text/plain", b"ok", "ok")
        log = sink.generate_log(response, 2)
        assert "Duration: 2.000s" in log
