# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: mistral_llm.py

"""
Mistral AI LLM component.

Connects to the Mistral AI API (La Plateforme) using the OpenAI-compatible
endpoint. Supports Mistral Large, Mistral Nemo, Codestral, and all models
available on La Plateforme.
"""

import logging
from typing import Any, Optional, Iterator, Union, AsyncIterator

from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

logger = logging.getLogger(__name__)

MISTRAL_MAX_CONTEXT_LENGTH = {
    "mistral-large-latest": 128000,
    "mistral-large-2407": 128000,
    "mistral-large-2411": 128000,
    "open-mistral-nemo": 128000,
    "open-mistral-7b": 32000,
    "open-mixtral-8x7b": 32000,
    "open-mixtral-8x22b": 64000,
    "codestral-latest": 32000,
    "codestral-2405": 32000,
    "mistral-small-latest": 32000,
    "mistral-small-2402": 32000,
    "mistral-tiny": 32000,
}


class MistralLLM(OpenAIStyleLLM):
    """Mistral AI LLM component.

    Connects to Mistral AI's OpenAI-compatible API endpoint.

    Attributes:
        api_key: Mistral API key (env: ``MISTRAL_API_KEY``).
        api_base: Mistral API base URL
            (default ``https://api.mistral.ai/v1``).
        proxy: Optional proxy URL (env: ``MISTRAL_PROXY``).
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("MISTRAL_API_KEY"))
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("MISTRAL_API_BASE")
        or "https://api.mistral.ai/v1")
    proxy: Optional[str] = Field(
        default_factory=lambda: get_from_env("MISTRAL_PROXY"))

    def _call(self, messages: list, **kwargs: Any) \
            -> Union[LLMOutput, Iterator[LLMOutput]]:
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) \
            -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        return await super()._acall(messages, **kwargs)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'MistralLLM':
        """Initialize the component from YAML, guarding unset ``${VAR}`` placeholders.

        YAML ``${VAR}`` placeholders resolve to an empty string when the
        environment variable is unset, so a copied ``mistral_llm.yaml.example``
        with a missing ``MISTRAL_API_KEY`` / ``MISTRAL_PROXY`` would otherwise
        assign ``''`` over the class defaults. That is worse than it sounds:
        the OpenAI client only rejects a *missing* key, so an empty key is
        silently sent upstream and surfaces as an opaque 401, and an empty
        ``api_base`` makes the client fall back to ``https://api.openai.com/v1``
        — sending Mistral credentials to the wrong endpoint. Normalizing the
        empty values here makes an unset variable behave exactly like an
        omitted key: ``api_key`` / ``proxy`` fall back to ``None`` and
        ``api_base`` to the Mistral endpoint.

        Args:
            component_configer (LLMConfiger): the LLM component configer.

        Returns:
            MistralLLM: the initialized instance.
        """
        super().initialize_by_component_configer(component_configer)
        if not self.api_key:
            self.api_key = None
        if not self.api_base:
            self.api_base = get_from_env("MISTRAL_API_BASE") or \
                "https://api.mistral.ai/v1"
        if not self.proxy:
            self.proxy = None
        return self

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return MISTRAL_MAX_CONTEXT_LENGTH.get(self.model_name, 32000)

    def get_num_tokens(self, text: str) -> int:
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            return super().get_num_tokens(text)
