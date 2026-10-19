# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_flask_request_log_sink.py

"""Unit tests for the FlaskRequestLogSink."""

from agentuniverse.base.util.logging.log_sink.flask_request_log_sink import     FlaskRequestLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestFlaskRequestLogSink:
    """Test flask request logging behavior."""

    def test_log_type(self):
        assert FlaskRequestLogSink().log_type ==             LogTypeEnum.flask_request

    def test_generate_log_returns_none(self):
        assert FlaskRequestLogSink().generate_log(flask_request="req") is None

    def test_process_record_pops_flask_request(self):
        sink = FlaskRequestLogSink()
        record = {"message": "x",
                  "extra": {"flask_request": "req",
                            "log_type": LogTypeEnum.flask_request}}
        sink.process_record(record)
        assert "flask_request" not in record["extra"]
        assert record["message"] is None
