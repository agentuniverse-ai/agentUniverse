# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/06
# @FileName: azure_openai_llm.py

from typing import Any, Optional, Union, Iterator, AsyncIterator

import httpx
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

AZURE_OPENAI_MAX_CONTEXT_LENGTH = {
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
    "gpt-35-turbo-1106": 16384,
    "gpt-35-turbo-0125": 16384,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "o1": 200000,
    "o1-mini": 128000,
    "o3-mini": 200000,
}


class AzureOpenAILLM(OpenAIStyleLLM):
    """Azure OpenAI LLM component.

    Uses AzureOpenAI client to interact with Azure-deployed OpenAI models.
    The model_name field maps to the Azure deployment name.
    The api_base field should be set to the Azure endpoint URL.

    Attributes:
        api_key: Azure OpenAI API key (env: AZURE_OPENAI_API_KEY).
        api_base: Azure OpenAI endpoint URL (env: AZURE_OPENAI_ENDPOINT).
        api_version: Azure OpenAI API version (default: 2024-10-21).
        proxy: Optional HTTP proxy.
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_API_KEY")
    )
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_ENDPOINT")
    )
    api_version: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_API_VERSION") or "2024-10-21"
    )
    proxy: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_PROXY")
    )
    organization: Optional[str] = None

    def _new_client(self):
        """Initialize the AzureOpenAI client."""
        if self.client is not None:
            return self.client
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.api_base,
            api_version=self.api_version,
            organization=self.organization,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )
        return self.client

    def _new_async_client(self):
        """Initialize the AsyncAzureOpenAI client."""
        if self.async_client is not None:
            return self.async_client
        from openai import AsyncAzureOpenAI
        self.async_client = AsyncAzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.api_base,
            api_version=self.api_version,
            organization=self.organization,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )
        return self.async_client

    def _call(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """The call method of the Azure OpenAI LLM.

        Args:
            messages: The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return super()._call(messages, **kwargs)

    async def _acall(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """The async call method of the Azure OpenAI LLM.

        Args:
            messages: The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Max context length for Azure-deployed OpenAI models."""
        if super().max_context_length():
            return super().max_context_length()
        return AZURE_OPENAI_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)

    def initialize_by_component_configer(self, component_configer) -> 'LLM':
        """Initialize from config, handling api_version field."""
        super().initialize_by_component_configer(component_configer)
        if component_configer.configer.value.get('api_version'):
            self.api_version = component_configer.configer.value.get('api_version')
        return self
