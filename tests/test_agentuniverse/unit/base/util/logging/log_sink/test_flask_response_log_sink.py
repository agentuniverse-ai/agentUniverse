# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_flask_response_log_sink.py

"""Unit tests for the FlaskResponseLogSink."""

from agentuniverse.base.util.logging.log_sink.flask_response_log_sink import     FlaskResponseLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestFlaskResponseLogSink:
    """Test flask response logging behavior."""

    def test_log_type(self):
        assert FlaskResponseLogSink().log_type ==             LogTypeEnum.flask_response

    def test_generate_log_returns_none(self):
        assert FlaskResponseLogSink().generate_log(
            flask_response="resp", elapsed_time=1.0) is None

    def test_process_record_pops_flask_response(self):
        sink = FlaskResponseLogSink()
        record = {"message": "x",
                  "extra": {"flask_response": "resp", "elapsed_time": 0.5,
                            "log_type": LogTypeEnum.flask_response}}
        sink.process_record(record)
        assert "flask_response" not in record["extra"]
        assert record["message"] is None
