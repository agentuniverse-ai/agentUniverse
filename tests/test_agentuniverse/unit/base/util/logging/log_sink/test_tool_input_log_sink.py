# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_tool_input_log_sink.py

"""Unit tests for the ToolInputLogSink."""

from agentuniverse.base.util.logging.log_sink.tool_input_log_sink import     ToolInputLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestToolInputLogSink:
    """Test tool input logging helpers."""

    def test_log_type(self):
        assert ToolInputLogSink().log_type == LogTypeEnum.tool_input

    def test_generate_log_contains_input(self):
        message = ToolInputLogSink().generate_log(tool_input="run python")
        assert "Tool input is run python" in message

    def test_process_record_sets_message(self):
        sink = ToolInputLogSink()
        record = {"message": "", "extra": {"tool_input": {"a": 1},
                                           "log_type": LogTypeEnum.tool_input}}
        sink.process_record(record)
        assert "Tool input is" in record["message"]
        assert "{'a': 1}" in record["message"]
