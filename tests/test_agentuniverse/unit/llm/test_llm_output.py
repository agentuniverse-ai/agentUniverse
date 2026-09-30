# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_llm_output.py
"""Unit tests for LLMOutput, TokenUsage and prune_none in llm_output."""

from agentuniverse.llm.llm_output import LLMOutput, TokenUsage, prune_none


class TestPruneNone:
    """Test the recursive prune_none helper."""

    def test_removes_none_entries(self):
        data = {"a": 1, "b": None, "c": {"d": None, "e": [None, 2]}}
        assert prune_none(data) == {"a": 1, "c": {"e": [2]}}

    def test_scalars_are_returned_unchanged(self):
        assert prune_none("text") == "text"
        assert prune_none(0) == 0


class TestTokenUsage:
    """Test TokenUsage parsing, aggregation and serialization."""

    def test_defaults_are_zero(self):
        usage = TokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_totals_sum_input_and_output(self):
        usage = TokenUsage(text_in=10, text_out=5, cached_in=2)
        assert usage.prompt_tokens == 12
        assert usage.completion_tokens == 5
        assert usage.total_tokens == 17

    def test_from_openai_chat_usage(self):
        usage = TokenUsage.from_openai({
            "prompt_tokens": 10,
            "completion_tokens": 6,
            "prompt_tokens_details": {"cached_tokens": 4},
        })
        assert usage.text_in == 10
        assert usage.cached_in == 4
        assert usage.text_out == 6

    def test_from_openai_empty_usage_returns_defaults(self):
        assert TokenUsage.from_openai({}) == TokenUsage()

    def test_addition_accumulates_fields(self):
        total = TokenUsage(text_in=1, text_out=2) + TokenUsage(text_in=3, text_out=4)
        assert total.prompt_tokens == 4
        assert total.completion_tokens == 6

    def test_to_dict_hides_zero_details_by_default(self):
        usage = TokenUsage(text_in=7, text_out=3)
        data = usage.to_dict()
        assert data["prompt_tokens"] == 7
        assert "cached_tokens" not in data["prompt_tokens_details"]

    def test_to_dict_keeps_zeros_when_requested(self):
        data = TokenUsage().to_dict(keep_zero=True)
        assert data["prompt_tokens_details"]["cached_tokens"] == 0


class TestLLMOutput:
    """Test LLMOutput flag helpers."""

    def test_stream_and_function_call_flags(self):
        assert LLMOutput(type="stream").is_stream()
        assert LLMOutput(type="tool_call").is_function_call()
        assert not LLMOutput(type="text").is_stream()
        assert not LLMOutput(type="text").is_function_call()
