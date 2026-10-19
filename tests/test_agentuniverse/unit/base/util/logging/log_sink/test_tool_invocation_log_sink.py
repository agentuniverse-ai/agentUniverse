# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 12:00
# @Author  : Yue Wang
# @FileName: test_tool_invocation_log_sink.py
"""Unit tests for ToolInvocationLogSink."""

from unittest.mock import patch

import pytest

from agentuniverse.base.util.logging.log_sink.tool_invocation_log_sink import \
    ToolInvocationLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


@pytest.fixture
def sink():
    """Create a ToolInvocationLogSink instance."""
    return ToolInvocationLogSink()


def _record(log_type=LogTypeEnum.tool_invocation, cost_time=0.5, tool_output="ok"):
    """Build a minimal loguru-style record."""
    return {"extra": {"log_type": log_type, "cost_time": cost_time,
                      "tool_output": tool_output}}


class TestToolInvocationLogSink:
    """Test ToolInvocationLogSink behavior."""

    def test_log_type(self, sink):
        """The sink handles the tool_invocation log type."""
        assert sink.log_type is LogTypeEnum.tool_invocation

    def test_generate_log_without_invocation_chain(self, sink):
        """Without an invocation chain the cost and output are logged plainly."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.tool_invocation_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = ""
            assert sink.generate_log(1.234, "result") == \
                " Tool cost 1.23 seconds Tool output is result"

    def test_generate_log_with_invocation_chain(self, sink):
        """The invocation chain string is prepended to the message."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.tool_invocation_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = "agent_1 | "
            assert sink.generate_log(0.5, None) == \
                "agent_1 |  Tool cost 0.50 seconds Tool output is None"

    def test_process_record_sets_message(self, sink):
        """process_record overwrites record['message'] with the generated log."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.tool_invocation_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = ""
            record = _record(cost_time=2.0, tool_output="done")
            sink.process_record(record)
        assert record["message"] == " Tool cost 2.00 seconds Tool output is done"

    def test_filter_accepts_matching_log_type(self, sink):
        """filter accepts tool_invocation records and sets the message."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.tool_invocation_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = ""
            record = _record()
            assert sink.filter(record) is True
        assert record["message"] == " Tool cost 0.50 seconds Tool output is ok"

    def test_filter_rejects_other_log_type(self, sink):
        """filter rejects records of other log types without touching the message."""
        record = _record(log_type=LogTypeEnum.default)
        assert sink.filter(record) is False
        assert "message" not in record
