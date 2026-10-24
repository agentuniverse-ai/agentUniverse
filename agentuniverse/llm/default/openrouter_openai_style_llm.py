# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : dxz0069
# @FileName: openrouter_openai_style_llm.py

from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

OPENROUTER_MAX_CONTEXT_LENGTH = {
    "openai/gpt-4o": 128000,
    "openai/gpt-4o-mini": 128000,
    "openai/gpt-4-turbo": 128000,
    "anthropic/claude-3.5-sonnet": 200000,
    "anthropic/claude-3.5-haiku": 200000,
    "google/gemini-flash-1.5": 1000000,
    "google/gemini-pro-1.5": 1000000,
    "meta-llama/llama-3.1-8b-instruct": 131072,
    "meta-llama/llama-3.1-70b-instruct": 131072,
    "mistralai/mistral-large": 131072,
    "deepseek/deepseek-chat": 65536,
}


class DefaultOpenRouterLLM(OpenAIStyleLLM):
    """The agentUniverse default OpenRouter llm module.

    OpenRouter (https://openrouter.ai) aggregates dozens of providers behind
    one OpenAI-compatible API; the model name selects both the model and the
    vendor, e.g. `openai/gpt-4o` or `anthropic/claude-3.5-sonnet`. Optional
    attribution headers (`HTTP-Referer`, `X-Title`) can be set through the
    `extra_headers` configuration.

    LLM parameters, such as name/description/model_name/max_tokens,
    are injected into this class by the default_openrouter_llm.yaml configuration.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_API_KEY"))
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("OPENROUTER_API_BASE") or OPENROUTER_API_BASE)

    def max_context_length(self) -> int:
        """Max context length.

        The total length of input tokens and generated tokens is limited by the model's context length.
        """
        if self._max_context_length:
            return self._max_context_length
        return OPENROUTER_MAX_CONTEXT_LENGTH.get(self.model_name, 8192)
