# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:50
# @Author  : yuewang
# @FileName: test_llm_output.py
"""Unit tests for LLMOutput, TokenUsage and prune_none."""

import pytest

from agentuniverse.llm.llm_output import (
    LLMOutput,
    TokenUsage,
    prune_none,
)


class TestPruneNone:
    """Test the prune_none helper."""

    def test_prunes_dict_and_list(self):
        data = {'a': 1, 'b': None, 'c': [1, None, 2], 'd': {'x': None, 'y': 3}}
        assert prune_none(data) == {'a': 1, 'c': [1, 2], 'd': {'y': 3}}

    def test_scalar_passthrough(self):
        assert prune_none('s') == 's'
        assert prune_none(5) == 5


class TestTokenUsage:
    """Test TokenUsage arithmetic and parsing."""

    def test_default_is_zero(self):
        usage = TokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_from_openai_chat_format(self):
        usage = TokenUsage.from_openai({'prompt_tokens': 10, 'completion_tokens': 5})
        assert usage.text_in == 10
        assert usage.text_out == 5
        assert usage.total_tokens == 15

    def test_from_openai_with_details(self):
        usage = TokenUsage.from_openai({
            'prompt_tokens': 10, 'completion_tokens': 5,
            'prompt_tokens_details': {'text_tokens': 8, 'cached_tokens': 2},
            'completion_tokens_details': {'text_tokens': 4, 'reasoning_tokens': 1}})
        assert (usage.text_in, usage.cached_in) == (8, 2)
        assert (usage.text_out, usage.reasoning_out) == (4, 1)
        assert (usage.cached_tokens, usage.reasoning_tokens, usage.completion_tokens) == (2, 1, 5)

    def test_from_openai_parses_realtime_singular_detail_keys(self):
        usage = TokenUsage.from_openai({
            'input_tokens': 13,
            'output_tokens': 9,
            'input_token_details': {
                'text_tokens': 8,
                'audio_tokens': 2,
                'cached_tokens': 3,
            },
            'output_token_details': {
                'text_tokens': 5,
                'audio_tokens': 4,
            },
        })

        assert usage.text_in == 8
        assert usage.audio_in == 2
        assert usage.cached_in == 3
        assert usage.text_out == 5
        assert usage.audio_out == 4

    def test_from_openai_parses_plural_output_detail_keys(self):
        usage = TokenUsage.from_openai({
            'input_tokens': 12,
            'output_tokens': 5,
            'input_tokens_details': {
                'text_tokens': 5,
                'image_tokens': 7,
            },
            'output_tokens_details': {
                'text_tokens': 1,
                'image_tokens': 4,
            },
        })

        assert usage.text_in == 5
        assert usage.image_in == 7
        assert usage.text_out == 1
        assert usage.image_out == 4

    def test_from_openai_empty_or_unknown(self):
        assert TokenUsage.from_openai(None).total_tokens == 0
        assert TokenUsage.from_openai({'weird': 1}).total_tokens == 0

    def test_to_dict_filters_zeros(self):
        usage = TokenUsage(text_in=3)
        d = usage.to_dict()
        assert d['prompt_tokens'] == 3
        assert 'prompt_tokens_details' in d
        assert 'completion_tokens_details' not in d
        d2 = usage.to_dict(keep_zero=True)
        assert 'completion_tokens_details' in d2


class TestLLMOutput:
    """Test LLMOutput type flags."""

    def test_defaults(self):
        out = LLMOutput()
        assert out.type == 'text'
        assert out.is_stream() is False
        assert out.is_function_call() is False

    def test_stream_and_function_call_flags(self):
        assert LLMOutput(type='stream').is_stream()
        assert LLMOutput(type='function_call').is_function_call()
        assert LLMOutput(type='tool_call').is_function_call()
        assert not LLMOutput(type='tool_call').is_stream()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
