# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/6
# @Author  : sien75
# @Email   : shaoning.shao@antgroup.com
# @FileName: openrouter_openai_style_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

OPENROUTER_MAX_CONTEXT_LENGTH = {
    "openai/gpt-5.1": 400000,
    "openai/gpt-5.1-codex": 400000,
    "openai/gpt-5-mini": 400000,
    "openai/gpt-5-nano": 400000,
    "anthropic/claude-sonnet-4.5": 1000000,
    "anthropic/claude-opus-4.5": 200000,
    "anthropic/claude-haiku-4.5": 200000,
    "google/gemini-3-pro-preview": 1048576,
    "google/gemini-2.5-flash": 1048576,
    "google/gemini-2.0-flash-001": 1048576,
    "x-ai/grok-4.1-fast:free": 2000000,
    "x-ai/grok-code-fast-1": 256000,
    "x-ai/grok-4-fast": 2000000,
    "qwen/qwen3-next-80b-a3b-instruct": 262144,
    "qwen/qwen3-235b-a22b-2507": 131072,
    "deepseek/deepseek-chat-v3.1": 163840,
    "deepseek/deepseek-chat-v3-0324": 163840,
    "minimax/minimax-m2": 204800,
    "z-ai/glm-4.6": 202752,
    "moonshotai/kimi-k2-thinking": 262144,
}


class OpenRouterOpenAIStyleLLM(OpenAIStyleLLM):
    """
    OpenRouter's OpenAI Style LLM
    
    OpenRouter provides unified access to multiple LLM providers through a single API.
    This class wraps OpenRouter's API using the OpenAI-compatible interface.
    
    Attributes:
        api_key (Optional[str]): The API key to use for authentication. Defaults to OPENROUTER_API_KEY env var.
        api_base (Optional[str]): The base URL to use for the API. Defaults to https://openrouter.ai/api/v1.
        proxy (Optional[str]): The proxy to use for requests. Defaults to OPENROUTER_PROXY env var.
        organization (Optional[str]): The organization ID. Defaults to OPENROUTER_ORGANIZATION env var.
    """
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env(
        "OPENROUTER_API_BASE"))
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_PROXY"))
    organization: Optional[str] = Field(default_factory=lambda: get_from_env("OPENROUTER_ORGANIZATION"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """ The call method of the LLM.

        Users can customize how the model interacts by overriding call method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """ The async call method of the LLM.

        Users can customize how the model interacts by overriding acall method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Get the max context length for the model.
        
        Returns:
            int: The maximum context length supported by the model.
        """
        if super().max_context_length():
            return super().max_context_length()
        return OPENROUTER_MAX_CONTEXT_LENGTH.get(self.model_name, 128000)

