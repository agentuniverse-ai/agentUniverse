# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_openai_style_langchain_instance.py
"""Unit tests for openai-style LangChain message/chunk conversions."""

import asyncio
from types import SimpleNamespace

import pytest

from agentuniverse.llm.openai_style_langchain_instance import (
    LangchainOpenAIStyleInstance,
    _convert_delta_to_message_chunk,
    convert_dict_to_message,
)


def make_llm(**overrides):
    attrs = dict(model_name="gpt-4o", temperature=0.3, request_timeout=None,
                 max_tokens=None, max_retries=2, streaming=False,
                 api_key="key", organization=None, api_base=None, proxy=None)
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


class TestConverters:
    """Test module-level dict/message conversion helpers."""

    def test_convert_user_dict_to_message(self):
        message = convert_dict_to_message({"role": "user", "content": "hello"})
        assert message.content == "hello"

    def test_convert_assistant_dict_with_reasoning(self):
        message = convert_dict_to_message({
            "role": "assistant", "content": "answer", "reasoning_content": "think",
        })
        assert message.content == "answer"
        assert message.additional_kwargs["reasoning_content"] == "think"

    def test_convert_tool_dict_to_message(self):
        message = convert_dict_to_message({
            "role": "tool", "content": "result", "tool_call_id": "t1",
        })
        assert message.tool_call_id == "t1"
        assert message.content == "result"

    def test_convert_missing_content_defaults_to_empty(self):
        message = convert_dict_to_message({"role": "assistant"})
        assert message.content == ""

    def test_delta_conversion_keeps_reasoning_content(self):
        chunk = _convert_delta_to_message_chunk(
            {"role": "assistant", "content": "a", "reasoning_content": "rc"}, None)
        assert chunk.additional_kwargs["reasoning_content"] == "rc"

    def test_delta_conversion_default_content(self):
        chunk = _convert_delta_to_message_chunk({"role": "assistant"}, None)
        assert chunk.content == ""


class TestLangchainOpenAIStyleInstance:
    """Test instance-level pure helpers."""

    def test_create_chat_result_parses_dict_response(self):
        instance = LangchainOpenAIStyleInstance(make_llm())
        result = instance._create_chat_result({
            "choices": [{"message": {"role": "assistant", "content": "Hi!"},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2},
            "system_fingerprint": "fp-1",
        })
        assert result.generations[0].message.content == "Hi!"
        assert result.llm_output["token_usage"]["prompt_tokens"] == 5
        assert result.llm_output["system_fingerprint"] == "fp-1"

    def test_as_langchain_achunk(self):
        async def astream():
            yield SimpleNamespace(raw={"choices": [{"delta": {"role": "assistant",
                                                              "content": "tok"}}]})

        async def collect():
            return [c.text async for c in
                    LangchainOpenAIStyleInstance.as_langchain_achunk(astream())]

        assert asyncio.run(collect()) == ["tok"]
