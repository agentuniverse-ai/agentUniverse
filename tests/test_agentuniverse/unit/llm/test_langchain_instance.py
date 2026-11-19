# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_langchain_instance.py
"""Unit tests for the LangchainOpenAI wrapper (no network access)."""

import asyncio
from types import SimpleNamespace

import pytest

from agentuniverse.llm.langchain_instance import LangchainOpenAI


def make_llm(**overrides):
    """Return a fake aU LLM object exposing the attributes read by the wrapper."""
    attrs = dict(model_name="gpt-4o", temperature=0.3, request_timeout=None,
                 max_tokens=None, max_retries=2, streaming=False,
                 openai_api_key="key", openai_organization=None,
                 openai_api_base=None, openai_proxy=None)
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


def delta_chunk(content, role="assistant", finish_reason=None):
    return SimpleNamespace(raw={"choices": [{"delta": {"role": role, "content": content},
                                             "finish_reason": finish_reason}]})


class TestLangchainOpenAI:
    """Test LangchainOpenAI mapping and chunk conversion."""

    def test_init_maps_llm_attributes(self):
        instance = LangchainOpenAI(make_llm())
        assert instance.model_name == "gpt-4o"
        assert instance.temperature == 0.3
        assert instance.llm is not None

    def test_init_applies_defaults_for_missing_attributes(self):
        instance = LangchainOpenAI(make_llm(model_name=None, temperature=None,
                                            streaming=None, openai_api_key=None))
        assert instance.model_name == "gpt-3.5-turbo"
        assert instance.temperature == 0.7
        assert instance.streaming is False
        assert instance.openai_api_key == "blank"

    def test_as_langchain_chunk_yields_text_chunks(self):
        stream = iter([delta_chunk("Hi"), delta_chunk(" there")])
        chunks = list(LangchainOpenAI.as_langchain_chunk(stream))
        assert [c.text for c in chunks] == ["Hi", " there"]

    def test_as_langchain_chunk_skips_empty_choices(self):
        stream = iter([delta_chunk("Hi"),
                       SimpleNamespace(raw={"choices": []}),
                       delta_chunk("!")])
        chunks = list(LangchainOpenAI.as_langchain_chunk(stream))
        assert [c.text for c in chunks] == ["Hi", "!"]

    def test_as_langchain_chunk_records_finish_reason(self):
        chunks = list(LangchainOpenAI.as_langchain_chunk(
            iter([delta_chunk("Hi", finish_reason="stop")])))
        assert chunks[0].generation_info == {"finish_reason": "stop"}

    def test_as_langchain_chunk_notifies_run_manager(self):
        seen = []

        class RunManager:
            def on_llm_new_token(self, token, chunk=None):
                seen.append(token)

        list(LangchainOpenAI.as_langchain_chunk(
            iter([delta_chunk("token-a"), delta_chunk("token-b")]),
            run_manager=RunManager()))
        assert seen == ["token-a", "token-b"]

    def test_as_langchain_achunk(self):
        async def astream():
            yield delta_chunk("async-token")

        async def collect():
            return [c.text async for c in LangchainOpenAI.as_langchain_achunk(astream())]

        assert asyncio.run(collect()) == ["async-token"]
