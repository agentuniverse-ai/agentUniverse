# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_agent_invocation_log_sink.py

"""Unit tests for the AgentInvocationLogSink."""

from types import SimpleNamespace

from agentuniverse.base.util.logging.log_sink.agent_invocation_log_sink import     AgentInvocationLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class FakeOutput:
    def to_json_str(self):
        return '{"content": "hello"}'


class TestAgentInvocationLogSink:
    """Test agent invocation logging helpers."""

    def test_log_type(self):
        assert AgentInvocationLogSink().log_type ==             LogTypeEnum.agent_invocation

    def test_generate_log_contains_cost_and_output(self):
        message = AgentInvocationLogSink().generate_log(
            cost_time=2.5, agent_output=FakeOutput())
        assert "Agent cost 2.50 seconds" in message
        assert "hello" in message

    def test_process_record_sets_message(self):
        sink = AgentInvocationLogSink()
        record = {"message": "",
                  "extra": {"cost_time": 1.0, "agent_output": FakeOutput(),
                            "log_type": LogTypeEnum.agent_invocation}}
        sink.process_record(record)
        assert "Agent cost 1.00 seconds" in record["message"]
