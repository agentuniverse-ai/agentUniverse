# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_agent_input_log_sink.py
"""Unit tests for AgentInputLogSink."""

from unittest.mock import patch

import pytest

from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.util.logging.log_sink.agent_input_log_sink import (
    AgentInputLogSink,
)
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum

_CHAIN = "agent->llm"


@pytest.fixture
def sink():
    """Create an AgentInputLogSink with a stubbed invocation chain."""
    return AgentInputLogSink()


class TestAgentInputLogSink:
    """Test AgentInputLogSink type markers and record handling."""

    def test_log_type_marker(self, sink):
        """The sink is tagged with the agent_input log type."""
        assert sink.log_type == LogTypeEnum.agent_input

    def test_component_type_marker(self, sink):
        """The sink reports the LOG_SINK component type."""
        assert sink.component_type == ComponentEnum.LOG_SINK

    def test_generate_log_string_input(self, sink):
        """generate_log embeds the string input after the chain prefix."""
        with patch(
                "agentuniverse.base.util.monitor.monitor."
                "Monitor.get_invocation_chain_str",
                return_value=_CHAIN):
            assert sink.generate_log("hi") == f"{_CHAIN} Agent input is hi"

    def test_process_record_sets_message(self, sink):
        """process_record writes the generated message onto the record."""
        record = {"extra": {"agent_input": "inp"}}
        with patch(
                "agentuniverse.base.util.monitor.monitor."
                "Monitor.get_invocation_chain_str",
                return_value=_CHAIN):
            sink.process_record(record)
        assert record["message"] == f"{_CHAIN} Agent input is inp"

    def test_process_record_missing_agent_input(self, sink):
        """A missing agent_input renders as None in the message."""
        record = {"extra": {}}
        with patch(
                "agentuniverse.base.util.monitor.monitor."
                "Monitor.get_invocation_chain_str",
                return_value=_CHAIN):
            sink.process_record(record)
        assert record["message"] == f"{_CHAIN} Agent input is None"

    def test_filter_matches_only_agent_input(self, sink):
        """filter accepts agent_input records and rejects others."""
        with patch(
                "agentuniverse.base.util.monitor.monitor."
                "Monitor.get_invocation_chain_str",
                return_value=_CHAIN):
            matching = {
                "extra": {"log_type": LogTypeEnum.agent_input,
                          "agent_input": "x"}}
            assert sink.filter(matching) is True
            assert "message" in matching

            other = {"extra": {"log_type": LogTypeEnum.default}}
            assert sink.filter(other) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
