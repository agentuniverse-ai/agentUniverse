# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:40
# @Author  : kaichuan
# @FileName: test_agent_first_token_log_sink.py
"""Unit tests for AgentFirstTokenLogSink in base.util.logging.log_sink."""

from unittest import mock

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.logging.log_sink.agent_first_token_log_sink import (
    AgentFirstTokenLogSink,
)
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestAgentFirstTokenLogSink:
    """Test log type, message generation, and record processing."""

    @pytest.fixture
    def sink(self):
        """Create a sink instance without registering any loguru sink."""
        return AgentFirstTokenLogSink()

    def test_log_type_is_agent_first_token(self, sink):
        """The sink is tagged with the agent_first_token log type."""
        assert sink.log_type == LogTypeEnum.agent_first_token

    def test_component_type(self, sink):
        """The sink reports the LOG_SINK component type."""
        assert sink.component_type == ComponentEnum.LOG_SINK

    def test_generate_log_formats_two_decimals(self, sink):
        """Cost time is rendered with exactly two decimal places."""
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.agent_first_token_log_sink."
            "Monitor.get_invocation_chain_str", return_value=""
        ):
            assert sink.generate_log(1.5) == " Agent first token cost 1.50 seconds."
            assert sink.generate_log(0.1) == " Agent first token cost 0.10 seconds."

    def test_generate_log_includes_invocation_chain(self, sink):
        """The invocation chain prefix is included in the message."""
        chain = "source: agent, type: AGENT | "
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.agent_first_token_log_sink."
            "Monitor.get_invocation_chain_str", return_value=chain
        ):
            message = sink.generate_log(2.0)
        assert message == f"{chain} Agent first token cost 2.00 seconds."

    def test_process_record_sets_message(self, sink):
        """process_record writes the generated message into the record."""
        record = {"extra": {"cost_time": 3.141}}
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.agent_first_token_log_sink."
            "Monitor.get_invocation_chain_str", return_value=""
        ):
            sink.process_record(record)
        assert record["message"] == " Agent first token cost 3.14 seconds."

    def test_filter_matches_only_own_log_type(self, sink):
        """filter passes records with the matching log_type and drops others."""
        matching = {"extra": {"log_type": LogTypeEnum.agent_first_token,
                              "cost_time": 1.0}}
        other = {"extra": {"log_type": LogTypeEnum.llm_invocation, "cost_time": 1.0}}
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.agent_first_token_log_sink."
            "Monitor.get_invocation_chain_str", return_value=""
        ):
            assert sink.filter(matching) is True
            assert matching["message"].startswith(" Agent first token cost")
            assert sink.filter(other) is False
            assert "message" not in other
