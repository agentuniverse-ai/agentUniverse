# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the custom Flask response log sink example.

``CustomFlaskResponseSink.generate_log`` formats a Flask response and its
elapsed time into a single log line; the response body is appended when the
data payload can be decoded.  All formatting logic is pure string handling.
"""

from types import SimpleNamespace

from examples.sample_standard_app.intelligence.utils.log_sink.custom_flask_response_sink import (
    CustomFlaskResponseSink,
)


class TestCustomFlaskResponseSink:
    def setup_method(self):
        self.sink = CustomFlaskResponseSink()

    def test_string_response_is_formatted_with_duration(self):
        line = self.sink.generate_log("hello world", 1.23456)
        assert line == "Response: hello world Duration: 1.235s"

    def test_response_object_includes_status_and_content_type(self):
        response = SimpleNamespace(
            status_code=200,
            content_type="text/html",
            data=b"<b>x</b>",
            get_data=lambda as_text=False: "<b>x</b>" if as_text else b"<b>x</b>",
        )
        line = self.sink.generate_log(response, 2.5)
        assert line == "Response: 200 text/html Duration: 2.500s Data:<b>x</b>"

    def test_response_object_without_data_omits_body(self):
        response = SimpleNamespace(
            status_code=204,
            content_type="text/html",
            data=None,
            get_data=lambda as_text=False: "",
        )
        line = self.sink.generate_log(response, 0.5)
        assert line == "Response: 204 text/html Duration: 0.500s"
        assert "Data:" not in line

    def test_duration_is_formatted_to_three_decimals(self):
        line = self.sink.generate_log("done", 0.1257)
        assert line.endswith("Duration: 0.126s")

    def test_get_data_failure_does_not_break_logging(self):
        class BoomResponse:
            status_code = 500
            content_type = "application/json"
            data = b"error"

            def get_data(self, as_text=False):
                raise RuntimeError("boom")

        line = self.sink.generate_log(BoomResponse(), 0.25)
        assert line == "Response: 500 application/json Duration: 0.250s"
        assert "Data:" not in line
