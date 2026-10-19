# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:45
# @Author  : kaichuan
# @FileName: test_llm_invocation_log_sink.py
"""Unit tests for LLMInvocationLogSink in base.util.logging.log_sink."""

from unittest import mock

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.logging.log_sink.llm_invocation_log_sink import (
    LLMInvocationLogSink,
)
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestLLMInvocationLogSink:
    """Test log type, message generation, and record processing."""

    @pytest.fixture
    def sink(self):
        """Create a sink instance without registering any loguru sink."""
        return LLMInvocationLogSink()

    def test_log_type_and_component_type(self, sink):
        """The sink carries the llm_invocation log type and LOG_SINK type."""
        assert sink.log_type == LogTypeEnum.llm_invocation
        assert sink.component_type == ComponentEnum.LOG_SINK

    def test_generate_log_without_tokens(self, sink):
        """Without token usage the message only reports the cost time."""
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.llm_invocation_log_sink."
            "Monitor.get_invocation_chain_str", return_value=""
        ):
            assert sink.generate_log(0, 1.5, "out") == \
                " LLM cost 1.50 seconds LLM output finished."

    def test_generate_log_with_tokens(self, sink):
        """A positive token count is included in the message."""
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.llm_invocation_log_sink."
            "Monitor.get_invocation_chain_str", return_value=""
        ):
            assert sink.generate_log(123, 0.25, "out") == \
                " LLM cost 0.25 seconds, token usage: 123 LLM output finished."

    def test_generate_log_includes_invocation_chain(self, sink):
        """The invocation chain prefix is included in the message."""
        chain = "source: llm, type: LLM | "
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.llm_invocation_log_sink."
            "Monitor.get_invocation_chain_str", return_value=chain
        ):
            message = sink.generate_log(7, 2.0, "out")
        assert message == \
            f"{chain} LLM cost 2.00 seconds, token usage: 7 LLM output finished."

    def test_process_record_sets_message(self, sink):
        """process_record writes the generated message into the record."""
        record = {"extra": {"used_token": 42, "cost_time": 0.5, "llm_output": "hi"}}
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.llm_invocation_log_sink."
            "Monitor.get_invocation_chain_str", return_value=""
        ):
            sink.process_record(record)
        assert record["message"] == \
            " LLM cost 0.50 seconds, token usage: 42 LLM output finished."

    def test_filter_matches_only_own_log_type(self, sink):
        """filter passes matching records and drops records of other types."""
        matching = {"extra": {"log_type": LogTypeEnum.llm_invocation,
                              "used_token": 1, "cost_time": 1.0}}
        other = {"extra": {"log_type": LogTypeEnum.agent_first_token,
                           "cost_time": 1.0}}
        with mock.patch(
            "agentuniverse.base.util.logging.log_sink.llm_invocation_log_sink."
            "Monitor.get_invocation_chain_str", return_value=""
        ):
            assert sink.filter(matching) is True
            assert matching["message"].startswith(" LLM cost 1.00 seconds")
            assert sink.filter(other) is False
            assert "message" not in other
