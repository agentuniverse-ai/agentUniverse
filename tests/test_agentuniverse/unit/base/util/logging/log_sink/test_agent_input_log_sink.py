# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_agent_input_log_sink.py

"""Unit tests for the AgentInputLogSink."""

from agentuniverse.base.util.logging.log_sink.agent_input_log_sink import     AgentInputLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestAgentInputLogSink:
    """Test agent input logging helpers."""

    def test_log_type(self):
        assert AgentInputLogSink().log_type == LogTypeEnum.agent_input

    def test_generate_log_contains_input(self):
        message = AgentInputLogSink().generate_log(agent_input="tell me")
        assert "Agent input is tell me" in message

    def test_process_record_sets_message(self):
        sink = AgentInputLogSink()
        record = {"message": "", "extra": {"agent_input": {"q": "hi"},
                                           "log_type": LogTypeEnum.agent_input}}
        sink.process_record(record)
        assert "Agent input is" in record["message"]
