# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/10 17:07
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_custom_flask_request_sink.py

"""Unit tests for the CustomFlaskRequestSink log sink."""

import pytest

from agentuniverse_extension.logger.log_sink.custom_flask_request_sink import \
    CustomFlaskRequestSink


class _FakeFlaskRequest:
    """Minimal stand-in for a Flask request object."""

    def __init__(self, method="GET", path="/api", headers=None, data=b"",
                 body_text="hello", raise_on_body=False):
        self.method = method
        self.path = path
        self.headers = headers or {"Content-Type": "application/json"}
        self.data = data
        self._body_text = body_text
        self._raise_on_body = raise_on_body

    def get_data(self, as_text=False):
        if self._raise_on_body:
            raise RuntimeError("read failed")
        if as_text:
            return self._body_text
        return self.data


@pytest.fixture
def sink():
    return CustomFlaskRequestSink()


class TestCustomFlaskRequestSink:
    """Tests for CustomFlaskRequestSink.generate_log."""

    def test_log_contains_method_path_headers(self, sink):
        req = _FakeFlaskRequest(method="POST", path="/search",
                                headers={"Accept": "application/json"})
        log = sink.generate_log(req)
        assert log.startswith("Request: POST /search Headers: {")
        assert "'Accept': 'application/json'" in log

    def test_log_includes_body_when_present(self, sink):
        req = _FakeFlaskRequest(method="PUT", data=b"some bytes",
                                body_text="raw payload")
        log = sink.generate_log(req)
        assert "Body: raw payload" in log

    def test_log_omits_body_when_empty(self, sink):
        req = _FakeFlaskRequest(data=b"")
        log = sink.generate_log(req)
        assert "Body:" not in log

    def test_log_survives_body_read_error(self, sink):
        req = _FakeFlaskRequest(data=b"x", raise_on_body=True)
        log = sink.generate_log(req)
        assert log.startswith("Request: GET /api")
        assert "Body:" not in log

    def test_process_record_sets_message(self, sink):
        req = _FakeFlaskRequest(method="DELETE", path="/items/1")
        record = {"extra": {"flask_request": req}}
        sink.process_record(record)
        assert record["message"].startswith("Request: DELETE /items/1")
        assert "flask_request" not in record["extra"]
