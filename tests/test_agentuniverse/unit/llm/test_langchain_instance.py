# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:45
# @Author  : yuewang
# @FileName: test_langchain_instance.py
"""Unit tests for LangchainOpenAI."""

from types import SimpleNamespace
from langchain_core.outputs import ChatGenerationChunk

from agentuniverse.llm.langchain_instance import LangchainOpenAI


class FakeAU_llm:
    """Minimal aU LLM-like object exposing the attributes used by LangchainOpenAI."""

    def __init__(self, **attrs):
        defaults = dict(model_name=None, temperature=None, request_timeout=30,
                        max_tokens=None, max_retries=None, streaming=None,
                        openai_api_key=None, openai_organization=None,
                        openai_api_base=None, openai_proxy=None)
        defaults.update(attrs)
        for k, v in defaults.items():
            setattr(self, k, v)


def _chunk_result(content, finish_reason=None):
    return SimpleNamespace(raw={'choices': [{'delta': {'role': 'assistant', 'content': content},
                                             'finish_reason': finish_reason}]})


class TestLangchainOpenAIInit:
    """Test the aU LLM attribute mapping in __init__."""

    def test_defaults_applied_when_attrs_missing(self):
        wrapper = LangchainOpenAI(FakeAU_llm())
        assert wrapper.model_name == 'gpt-3.5-turbo'
        assert wrapper.temperature == 0.7
        assert wrapper.max_retries == 2
        assert wrapper.streaming is False
        assert wrapper.openai_api_key == 'blank'

    def test_explicit_values_are_kept(self):
        wrapper = LangchainOpenAI(FakeAU_llm(model_name='gpt-4o', temperature=0.2,
                                             max_retries=5, streaming=True,
                                             openai_api_key='sk-test'))
        assert (wrapper.model_name, wrapper.temperature, wrapper.max_retries) == ('gpt-4o', 0.2, 5)
        assert wrapper.streaming is True
        assert wrapper.openai_api_key == 'sk-test'

    def test_llm_reference_stored(self):
        llm = FakeAU_llm()
        assert LangchainOpenAI(llm).llm is llm


class TestLangchainOpenAICHunks:
    """Test the chunk stream conversion helpers."""

    def test_as_langchain_chunk_yields_message_chunks(self):
        stream = iter([_chunk_result('he'), _chunk_result('llo', 'stop')])
        chunks = list(LangchainOpenAI.as_langchain_chunk(stream))
        assert len(chunks) == 2
        assert all(isinstance(c, ChatGenerationChunk) for c in chunks)
        assert chunks[0].text == 'he'
        assert chunks[1].generation_info == {'finish_reason': 'stop'}

    def test_as_langchain_chunk_skips_empty_choices(self):
        empty = SimpleNamespace(raw={'choices': []})
        chunks = list(LangchainOpenAI.as_langchain_chunk(iter([empty, _chunk_result('x')])))
        assert len(chunks) == 1
        assert chunks[0].text == 'x'

    def test_as_langchain_achunk(self):
        import asyncio

        async def gen():
            yield _chunk_result('a')
            yield _chunk_result('b', 'stop')

        async def collect():
            return [c async for c in LangchainOpenAI.as_langchain_achunk(gen())]

        chunks = asyncio.run(collect())
        assert [c.text for c in chunks] == ['a', 'b']
        assert chunks[1].generation_info == {'finish_reason': 'stop'}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
