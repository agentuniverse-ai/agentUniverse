# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_agent_invocation_log_sink.py
"""Unit tests for AgentInvocationLogSink."""

import json
from unittest.mock import patch

import pytest

from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.logging.log_sink.agent_invocation_log_sink import (
    AgentInvocationLogSink,
)
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestAgentInvocationLogSink:
    """Test AgentInvocationLogSink log generation and filtering."""

    @pytest.fixture
    def sink(self):
        """Create a sink and stub the invocation chain to keep output stable."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.agent_invocation_log_sink."
            "Monitor.get_invocation_chain_str",
            return_value="",
        ):
            yield AgentInvocationLogSink()

    def test_log_type_is_agent_invocation(self):
        """The sink declares the agent_invocation log type."""
        assert AgentInvocationLogSink().log_type == LogTypeEnum.agent_invocation

    def test_generate_log_formats_cost_and_output(self, sink):
        """generate_log embeds the formatted cost time and JSON output."""
        output = OutputObject({"result": "hi"})
        log = sink.generate_log(1.234, output)
        assert " Agent cost 1.23 seconds" in log
        assert f" Agent output is {json.dumps(output.to_dict())}" in log

    def test_process_record_sets_message(self, sink):
        """process_record stores the generated log in record['message']."""
        record = {"extra": {"cost_time": 0.5,
                            "agent_output": OutputObject({"ok": True})}}
        sink.process_record(record)
        assert record["message"] == " Agent cost 0.50 seconds Agent output is " \
            + json.dumps({"ok": True})

    def test_filter_matches_only_its_log_type(self, sink):
        """filter returns True and processes only its own log type."""
        matched = {"extra": {"log_type": LogTypeEnum.agent_invocation,
                             "cost_time": 1.0,
                             "agent_output": OutputObject({})}}
        assert sink.filter(matched) is True
        assert "message" in matched
        other = {"extra": {"log_type": LogTypeEnum.llm_input}}
        assert sink.filter(other) is False
        assert "message" not in other

    def test_get_inheritance_depth(self):
        """get_inheritance_depth reflects the MRO position of LogSink."""
        assert AgentInvocationLogSink().get_inheritance_depth() == 2
