# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:10
# @Author  : yuewang
# @FileName: test_default_channel_langchain_instance.py
"""Unit tests for DefaultChannelLangchainInstance."""

from langchain_core.messages import (AIMessage, AIMessageChunk, ChatMessage,
    HumanMessage, HumanMessageChunk, SystemMessage, ToolMessage, ToolMessageChunk)
from langchain_core.outputs import ChatResult

from agentuniverse.llm.llm_channel.langchain_instance.default_channel_langchain_instance import (
    DefaultChannelLangchainInstance,
)


class FakeChannel:
    """Minimal LLMChannel-like object with the attributes the wrapper reads."""

    def __init__(self, **attrs):
        defaults = dict(channel_model_name='test-model', temperature=None, request_timeout=30,
                        max_tokens=None, max_retries=None, streaming=None, channel_api_key=None,
                        channel_organization=None, channel_api_base=None, channel_proxy=None)
        for k, v in {**defaults, **attrs}.items():
            setattr(self, k, v)

    def get_num_tokens(self, text):
        return len(text)


class TestInitMapping:
    """Test the channel attribute mapping in __init__."""

    def test_defaults_applied(self):
        w = DefaultChannelLangchainInstance(FakeChannel())
        assert w.model_name == 'test-model'
        assert (w.temperature, w.max_retries, w.streaming, w.openai_api_key) == (0.7, 2, False, 'blank')

    def test_explicit_values_kept(self):
        w = DefaultChannelLangchainInstance(FakeChannel(temperature=0.3, max_retries=3,
                                                        streaming=True, channel_api_key='sk-x'))
        assert (w.temperature, w.max_retries, w.streaming) == (0.3, 3, True)
        assert w.openai_api_key == 'sk-x'
        assert w.llm_channel is not None


class TestMessageConversion:
    """Test dict->message and delta->chunk conversion."""

    def test_convert_dict_to_message_roles(self):
        w = DefaultChannelLangchainInstance(FakeChannel())
        assert isinstance(w.convert_dict_to_message({'role': 'user', 'content': 'u'}), HumanMessage)
        assert isinstance(w.convert_dict_to_message({'role': 'assistant', 'content': 'a'}), AIMessage)
        assert isinstance(w.convert_dict_to_message({'role': 'system', 'content': 's'}), SystemMessage)
        tool = w.convert_dict_to_message(
            {'role': 'tool', 'content': 't', 'tool_call_id': 'c1', 'name': 'n'})
        assert isinstance(tool, ToolMessage) and tool.tool_call_id == 'c1'
        assert isinstance(w.convert_dict_to_message({'role': 'weird', 'content': 'c'}), ChatMessage)

    def test_convert_delta_to_message_chunk(self):
        w = DefaultChannelLangchainInstance(FakeChannel())
        assert isinstance(
            w._convert_delta_to_message_chunk({'role': 'assistant', 'content': 'x'}, AIMessageChunk),
            AIMessageChunk)
        assert isinstance(
            w._convert_delta_to_message_chunk({'role': 'user', 'content': 'y'}, AIMessageChunk),
            HumanMessageChunk)
        tool = w._convert_delta_to_message_chunk(
            {'role': 'tool', 'content': 'z', 'tool_call_id': 'tc1'}, ToolMessageChunk)
        assert isinstance(tool, ToolMessageChunk) and tool.tool_call_id == 'tc1'

    def test_create_chat_result(self):
        w = DefaultChannelLangchainInstance(FakeChannel())
        response = {'choices': [{'message': {'role': 'assistant', 'content': 'hi'},
                                 'finish_reason': 'stop'}],
                    'usage': {'prompt_tokens': 1, 'completion_tokens': 2}}
        result = w._create_chat_result(response)
        assert isinstance(result, ChatResult)
        assert result.generations[0].message.content == 'hi'
        assert result.llm_output['token_usage']['prompt_tokens'] == 1



if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
