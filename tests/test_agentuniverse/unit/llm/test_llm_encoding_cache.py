#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import threading
from unittest.mock import patch

import tiktoken

from agentuniverse.llm.llm import LLM
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

SPECIAL_TOKEN_TEXT = "policy excerpt <|endoftext|> continues <|endofprompt|> done"


class EncodingCountingLLM(LLM):
    """Minimal concrete LLM exercising the shared token counting implementation."""

    def _call(self, *args, **kwargs):
        return None

    async def _acall(self, *args, **kwargs):
        return None

    def get_num_tokens(self, text: str) -> int:
        return super().get_num_tokens(text)


def _clear_encoding_cache():
    from agentuniverse.llm import llm as llm_module
    getattr(llm_module, "_ENCODING_CACHE", {}).clear()


def test_known_model_encoding_is_resolved_once():
    _clear_encoding_cache()
    llm = EncodingCountingLLM(name="counting_llm", model_name="gpt-4o")
    with patch("tiktoken.encoding_for_model", wraps=tiktoken.encoding_for_model) as resolve:
        counts = [llm.get_num_tokens("hello agentuniverse") for _ in range(5)]
    assert len(set(counts)) == 1
    assert resolve.call_count == 1


def test_unknown_model_falls_back_to_cl100k_base_once():
    _clear_encoding_cache()
    llm = EncodingCountingLLM(name="counting_llm", model_name="qwen-max")
    expected = len(tiktoken.get_encoding("cl100k_base").encode("hello agentuniverse"))
    with patch("tiktoken.encoding_for_model", wraps=tiktoken.encoding_for_model) as resolve, \
            patch("tiktoken.get_encoding", wraps=tiktoken.get_encoding) as fallback:
        counts = [llm.get_num_tokens("hello agentuniverse") for _ in range(3)]
    assert counts == [expected] * 3
    assert resolve.call_count == 1
    assert fallback.call_count == 1


def test_openai_style_llm_shares_the_cached_resolution():
    _clear_encoding_cache()
    llm = OpenAIStyleLLM(name="openai_style_llm", model_name="gpt-4o", api_key="ak")
    with patch("tiktoken.encoding_for_model", wraps=tiktoken.encoding_for_model) as resolve:
        first = llm.get_num_tokens("hello agentuniverse")
        second = llm.get_num_tokens("hello agentuniverse")
    assert first == second > 0
    assert resolve.call_count == 1


def test_special_tokens_do_not_break_token_counting():
    _clear_encoding_cache()
    for model_name in ("gpt-4o", "qwen-max"):
        llm = EncodingCountingLLM(name="counting_llm", model_name=model_name)
        assert llm.get_num_tokens(SPECIAL_TOKEN_TEXT) > 0


def test_token_counts_match_direct_tiktoken_encoding():
    _clear_encoding_cache()
    llm = EncodingCountingLLM(name="counting_llm", model_name="gpt-4o")
    text = "请对以下保险条款进行总结，并输出关键风险点。"
    direct = len(tiktoken.encoding_for_model("gpt-4o").encode(text))
    assert llm.get_num_tokens(text) == direct


def test_concurrent_token_counting_resolves_encoding_once():
    _clear_encoding_cache()
    llm = EncodingCountingLLM(name="counting_llm", model_name="gpt-4o")
    results = []
    errors = []

    def count_repeatedly():
        try:
            results.append(sum(llm.get_num_tokens("threaded token counting") for _ in range(25)))
        except Exception as exc:
            errors.append(exc)

    with patch("tiktoken.encoding_for_model", wraps=tiktoken.encoding_for_model) as resolve:
        threads = [threading.Thread(target=count_repeatedly) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    assert errors == []
    assert len(results) == 8
    assert len(set(results)) == 1
    assert resolve.call_count == 1
