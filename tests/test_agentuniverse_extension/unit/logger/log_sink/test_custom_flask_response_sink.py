# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for agentuniverse_extension.logger.log_sink.custom_flask_response_sink."""
import pytest

from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum
from agentuniverse_extension.logger.log_sink.custom_flask_response_sink import CustomFlaskResponseSink


class _FakeResponse:
    """Minimal stand-in for a Flask response object."""

    def __init__(self, status_code=200, content_type="application/json", data=b'{"ok": true}'):
        self.status_code = status_code
        self.content_type = content_type
        self.data = data

    def get_data(self, as_text=True):
        return self.data.decode("utf-8") if as_text else self.data


class TestCustomFlaskResponseSink:
    """Tests for the CustomFlaskResponseSink log generation."""

    @pytest.fixture
    def sink(self):
        return CustomFlaskResponseSink()

    def test_generate_log_with_string_response(self, sink):
        result = sink.generate_log("hello world", 1.23456)
        assert result == "Response: hello world Duration: 1.235s"

    def test_generate_log_with_response_object(self, sink):
        response = _FakeResponse()
        result = sink.generate_log(response, 2.5)
        assert result == 'Response: 200 application/json Duration: 2.500s Data:{"ok": true}'

    def test_generate_log_without_body_data(self, sink):
        response = _FakeResponse(status_code=500, content_type="text/plain", data=b"")
        result = sink.generate_log(response, 0.25)
        assert result == "Response: 500 text/plain Duration: 0.250s"

    def test_generate_log_ignores_get_data_failure(self, sink):
        class _BrokenResponse(_FakeResponse):
            def get_data(self, as_text=True):
                raise RuntimeError("cannot read body")

        result = sink.generate_log(_BrokenResponse(), 1.0)
        assert result == "Response: 200 application/json Duration: 1.000s"

    def test_sink_log_type_is_flask_response(self, sink):
        assert sink.log_type == LogTypeEnum.flask_response

    def test_process_record_builds_message_and_cleans_extra(self, sink):
        record = {
            "message": None,
            "extra": {
                "log_type": LogTypeEnum.flask_response,
                "flask_response": "hi",
                "elapsed_time": 1.25,
            },
        }
        assert sink.filter(record) is True
        assert record["message"] == "Response: hi Duration: 1.250s"
        assert "flask_response" not in record["extra"]
