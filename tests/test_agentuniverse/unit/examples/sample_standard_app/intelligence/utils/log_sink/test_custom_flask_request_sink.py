# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_custom_flask_request_sink.py
"""Unit tests for the CustomFlaskRequestSink log sink example.

The example formats an incoming Flask request into a single log line
including the method, the path, the headers and, when available, the body.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[8]))

from agentuniverse.base.util.logging.log_sink.flask_request_log_sink import \
    FlaskRequestLogSink
from examples.sample_standard_app.intelligence.utils.log_sink.custom_flask_request_sink import \
    CustomFlaskRequestSink


class _FakeFlaskRequest:
    """Minimal stand-in for a Flask request used by ``generate_log``."""

    def __init__(self, method="GET", path="/", headers=None, data=b"",
                 body_text=""):
        self.method = method
        self.path = path
        self.headers = headers if headers is not None else {}
        self.data = data
        self._body_text = body_text

    def get_data(self, as_text=False):
        return self._body_text


class _BrokenBodyRequest(_FakeFlaskRequest):
    """Request whose body extraction always fails."""

    def get_data(self, as_text=False):
        raise RuntimeError("body extraction failed")


class TestCustomFlaskRequestSink:
    """Test the CustomFlaskRequestSink example sink."""

    @pytest.fixture
    def sink(self) -> CustomFlaskRequestSink:
        return CustomFlaskRequestSink()

    def test_is_flask_request_log_sink(self):
        assert issubclass(CustomFlaskRequestSink, FlaskRequestLogSink)

    def test_log_contains_method_and_path(self, sink):
        request = _FakeFlaskRequest(method="POST", path="/api/v1/health")
        log = sink.generate_log(request)
        assert "Request: POST /api/v1/health" in log

    def test_headers_are_included_as_dict(self, sink):
        request = _FakeFlaskRequest(headers={"Accept": "application/json"})
        log = sink.generate_log(request)
        assert "Headers:" in log
        assert "Accept" in log and "application/json" in log

    def test_no_body_when_request_data_empty(self, sink):
        request = _FakeFlaskRequest(data=b"")
        log = sink.generate_log(request)
        assert "Body:" not in log

    def test_body_included_when_request_has_data(self, sink):
        request = _FakeFlaskRequest(data=b"payload", body_text="payload")
        log = sink.generate_log(request)
        assert "Body: payload" in log

    def test_log_is_string(self, sink):
        request = _FakeFlaskRequest()
        assert isinstance(sink.generate_log(request), str)

    def test_body_error_is_swallowed(self, sink):
        request = _BrokenBodyRequest(data=b"payload")
        log = sink.generate_log(request)
        assert "Body:" not in log
        assert log.startswith("Request: GET /")
