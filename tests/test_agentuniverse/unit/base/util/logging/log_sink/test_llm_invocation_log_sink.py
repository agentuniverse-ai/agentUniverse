# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_llm_invocation_log_sink.py

"""Unit tests for the LLMInvocationLogSink."""

from agentuniverse.base.util.logging.log_sink.llm_invocation_log_sink import     LLMInvocationLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestLLMInvocationLogSink:
    """Test llm invocation logging helpers."""

    def test_log_type(self):
        assert LLMInvocationLogSink().log_type ==             LogTypeEnum.llm_invocation

    def test_generate_log_with_token_usage(self):
        message = LLMInvocationLogSink().generate_log(
            used_token=128, cost_time=1.5, llm_output="text")
        assert "LLM cost 1.50 seconds" in message
        assert "token usage: 128" in message
        assert "LLM output finished." in message

    def test_generate_log_without_token_usage(self):
        message = LLMInvocationLogSink().generate_log(
            used_token=None, cost_time=1.5, llm_output="text")
        assert "token usage" not in message

    def test_process_record_sets_message(self):
        sink = LLMInvocationLogSink()
        record = {"message": "", "extra": {"used_token": 5, "cost_time": 2.0,
                                           "llm_output": "x",
                                           "log_type": LogTypeEnum.llm_invocation}}
        sink.process_record(record)
        assert "token usage: 5" in record["message"]
