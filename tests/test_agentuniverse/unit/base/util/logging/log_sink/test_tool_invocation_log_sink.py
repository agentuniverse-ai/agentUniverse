# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_tool_invocation_log_sink.py

"""Unit tests for the ToolInvocationLogSink."""

from agentuniverse.base.util.logging.log_sink.tool_invocation_log_sink import     ToolInvocationLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestToolInvocationLogSink:
    """Test tool invocation logging helpers."""

    def test_log_type(self):
        assert ToolInvocationLogSink().log_type ==             LogTypeEnum.tool_invocation

    def test_generate_log_contains_cost_and_output(self):
        message = ToolInvocationLogSink().generate_log(cost_time=3.0,
                                                       tool_output="ok")
        assert "Tool cost 3.00 seconds" in message
        assert "Tool output is ok" in message

    def test_process_record_sets_message(self):
        sink = ToolInvocationLogSink()
        record = {"message": "", "extra": {"cost_time": 0.75,
                                           "tool_output": "done",
                                           "log_type": LogTypeEnum.tool_invocation}}
        sink.process_record(record)
        assert "Tool cost 0.75 seconds" in record["message"]
