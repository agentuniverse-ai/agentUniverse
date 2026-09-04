# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_llm_input_log_sink.py

"""Unit tests for the LLMInputLogSink."""

from agentuniverse.base.util.logging.log_sink.llm_input_log_sink import     LLMInputLogSink
from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestLLMInputLogSink:
    """Test llm input logging helpers."""

    def test_log_type(self):
        assert LLMInputLogSink().log_type == LogTypeEnum.llm_input

    def test_generate_log_static_message(self):
        message = LLMInputLogSink().generate_log(llm_input="ignored")
        assert "LLM get an input." in message

    def test_process_record_sets_message(self):
        sink = LLMInputLogSink()
        record = {"message": "", "extra": {"llm_input": "hello",
                                           "log_type": LogTypeEnum.llm_input}}
        sink.process_record(record)
        assert "LLM get an input." in record["message"]
