# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 11:30
# @Author  : Yue Wang
# @FileName: test_llm_input_log_sink.py
"""Unit tests for LLMInputLogSink."""

from unittest.mock import patch

import pytest

from agentuniverse.base.util.logging.log_sink.llm_input_log_sink import LLMInputLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


@pytest.fixture
def sink():
    """Create an LLMInputLogSink instance."""
    return LLMInputLogSink()


def _record(log_type=LogTypeEnum.llm_input, llm_input="hello"):
    """Build a minimal loguru-style record."""
    return {"extra": {"log_type": log_type, "llm_input": llm_input}}


class TestLLMInputLogSink:
    """Test LLMInputLogSink behavior."""

    def test_log_type(self, sink):
        """The sink handles the llm_input log type."""
        assert sink.log_type is LogTypeEnum.llm_input

    def test_generate_log_without_invocation_chain(self, sink):
        """Without an invocation chain the message is the plain prefix."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.llm_input_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = ""
            assert sink.generate_log("any input") == " LLM get an input."

    def test_generate_log_with_invocation_chain(self, sink):
        """The invocation chain string is prepended to the message."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.llm_input_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = "agent_1 | "
            assert sink.generate_log(None) == "agent_1 |  LLM get an input."

    def test_process_record_sets_message(self, sink):
        """process_record overwrites record['message'] with the generated log."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.llm_input_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = ""
            record = _record(llm_input={"input": "hi"})
            sink.process_record(record)
        assert record["message"] == " LLM get an input."

    def test_filter_accepts_matching_log_type(self, sink):
        """filter accepts records of the llm_input log type and sets the message."""
        with patch(
            "agentuniverse.base.util.logging.log_sink.llm_input_log_sink.Monitor"
        ) as mock_monitor:
            mock_monitor.get_invocation_chain_str.return_value = ""
            record = _record()
            assert sink.filter(record) is True
        assert record["message"] == " LLM get an input."

    def test_filter_rejects_other_log_type(self, sink):
        """filter rejects records of other log types without touching the message."""
        record = _record(log_type=LogTypeEnum.default)
        assert sink.filter(record) is False
        assert "message" not in record
