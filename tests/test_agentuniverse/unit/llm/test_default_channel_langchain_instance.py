# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_default_channel_langchain_instance.py
"""Unit tests for DefaultChannelLangchainInstance conversions (offline)."""

import asyncio
from types import SimpleNamespace

import pytest

from agentuniverse.llm.llm_channel.langchain_instance.default_channel_langchain_instance import (
    DefaultChannelLangchainInstance,
)


def make_channel(**overrides):
    attrs = dict(channel_model_name="gpt-4o", temperature=0.3, request_timeout=None,
                 max_tokens=None, max_retries=2, streaming=False, channel_api_key=None,
                 channel_organization=None, channel_api_base=None, channel_proxy=None)
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


def raw_chunk(content, role="assistant", finish_reason=None):
    return SimpleNamespace(raw={"choices": [{"delta": {"role": role, "content": content},
                                             "finish_reason": finish_reason}]})


class TestDefaultChannelLangchainInstance:
    """Test message conversion and chunk handling."""

    def test_init_maps_channel_attributes(self):
        instance = DefaultChannelLangchainInstance(make_channel())
        assert instance.model_name == "gpt-4o"
        assert instance.openai_api_key == "blank"

    def test_init_keeps_existing_api_key(self):
        instance = DefaultChannelLangchainInstance(make_channel(channel_api_key="real"))
        assert instance.openai_api_key == "real"

    def test_as_langchain_chunk_yields_text(self):
        instance = DefaultChannelLangchainInstance(make_channel())
        chunks = list(instance.as_langchain_chunk(iter([
            raw_chunk("Hello"), raw_chunk(" world"),
        ])))
        assert [c.text for c in chunks] == ["Hello", " world"]

    def test_as_langchain_chunk_skips_empty_choices(self):
        instance = DefaultChannelLangchainInstance(make_channel())
        stream = iter([raw_chunk("A"), SimpleNamespace(raw={"choices": []}), raw_chunk("B")])
        assert [c.text for c in list(instance.as_langchain_chunk(stream))] == ["A", "B"]

    def test_convert_dict_to_message_handles_tool_role(self):
        instance = DefaultChannelLangchainInstance(make_channel())
        msg = instance.convert_dict_to_message(
            {"role": "tool", "content": "result", "tool_call_id": "t-1"})
        assert msg.tool_call_id == "t-1"
        assert msg.content == "result"

    def test_create_chat_result_parses_response(self):
        instance = DefaultChannelLangchainInstance(make_channel())
        result = instance._create_chat_result({
            "choices": [{"message": {"role": "assistant", "content": "ok"},
                         "finish_reason": "stop"}],
            "usage": {"total_tokens": 3},
        })
        assert result.generations[0].message.content == "ok"
        assert result.llm_output["token_usage"] == {"total_tokens": 3}
