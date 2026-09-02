# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:15
# @Author  : yuewang
# @FileName: test_llm_channel.py
"""Unit tests for LLMChannel."""

from types import SimpleNamespace

from agentuniverse.base.component.component_enum import ComponentEnum

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage


def _configer(value=None):
    return SimpleNamespace(channel_name='ch1', channel_api_key='k', channel_api_base='http://base',
                           channel_model_name='m1', model_support_stream=True,
                           model_support_max_tokens=100, model_support_max_context_length=1000,
                           configer=SimpleNamespace(value=value or {}))


class TestLLMChannelInit:
    """Test defaults and configer-based initialization."""

    def test_defaults(self):
        ch = LLMChannel()
        assert ch.component_type == ComponentEnum.LLM_CHANNEL
        assert ch.model_is_openai_protocol_compatible is True
        assert ch.channel_name is None
        assert ch.ext_headers == {} and ch.ext_params == {}

    def test_initialize_by_component_configer(self):
        ch = LLMChannel()
        result = ch._initialize_by_component_configer(
            _configer({'extra_headers': {'h': '1'}, 'extra_params': {'p': 2}}))
        assert result is ch
        assert (ch.channel_name, ch.channel_model_name, ch.model_support_max_tokens) == ('ch1', 'm1', 100)
        assert ch.ext_headers == {'h': '1'}
        assert ch.ext_params == {'p': 2, 'stream_options': {'include_usage': True}}


class TestChannelModelConfigSetter:
    """Test the channel_model_config setter logic."""

    def test_sets_missing_attrs_and_caps_max_tokens(self):
        ch = LLMChannel()
        ch.model_support_max_tokens = 50
        ch.channel_model_config = {'temperature': 0.4, 'max_tokens': 80,
                                   'max_context_length': 4096}
        assert ch.__dict__['temperature'] == 0.4
        assert ch.__dict__['max_tokens'] == 50
        assert ch.__dict__['max_context_length'] == 4096

    def test_streaming_forced_off_when_unsupported(self):
        ch = LLMChannel()
        ch.model_support_stream = False
        ch.channel_model_config = {'streaming': True}
        assert ch.__dict__['streaming'] is False



class TestLLMChannelParseResult:
    """Test parse_result for stream chunks."""

    @staticmethod
    def _chunk(dumped):
        return SimpleNamespace(model_dump=lambda: dumped)

    def test_parse_result_with_choices(self):
        out = LLMChannel.parse_result(self._chunk(
            {'choices': [{'delta': {'content': 'hi', 'role': 'assistant'}}],
             'usage': {'prompt_tokens': 3, 'completion_tokens': 1}}))
        assert isinstance(out, LLMOutput)
        assert out.text == 'hi'
        assert out.message.type == 'assistant'
        assert isinstance(out.usage, TokenUsage)
        assert out.usage.prompt_tokens == 3




if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
