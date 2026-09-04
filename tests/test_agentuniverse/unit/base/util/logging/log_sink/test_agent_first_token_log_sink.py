# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_agent_first_token_log_sink.py

"""Unit tests for the AgentFirstTokenLogSink."""

from agentuniverse.base.util.logging.log_sink.agent_first_token_log_sink import     AgentFirstTokenLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestAgentFirstTokenLogSink:
    """Test agent first-token logging helpers."""

    def test_log_type(self):
        assert AgentFirstTokenLogSink().log_type ==             LogTypeEnum.agent_first_token

    def test_generate_log_formats_cost(self):
        message = AgentFirstTokenLogSink().generate_log(cost_time=1.239)
        assert "Agent first token cost 1.24 seconds." in message

    def test_process_record_sets_message(self):
        sink = AgentFirstTokenLogSink()
        record = {"message": "", "extra": {"cost_time": 0.5,
                                           "log_type": LogTypeEnum.agent_first_token}}
        sink.process_record(record)
        assert "Agent first token cost 0.50 seconds." in record["message"]
