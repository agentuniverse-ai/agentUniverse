# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: azure_openai_llm.py
from typing import Any, Optional, Iterator, Union, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

AZURE_OPENAI_MAX_CONTEXT_LENGTH = {
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
    "gpt-35-turbo-0301": 4096,
    "gpt-35-turbo-0613": 4096,
    "gpt-35-turbo-1106": 16384,
    "gpt-35-turbo-0125": 16384,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4o-2024-05-13": 128000,
    "gpt-4o-mini-2024-07-18": 128000,
    "o1-preview": 128000,
    "o1-mini": 128000,
}


class AzureOpenAILLM(OpenAIStyleLLM):
    """Azure OpenAI LLM component.

    Connects to Azure OpenAI Service using the Azure-specific endpoint and
    deployment model. Requires ``deployment_name``, ``azure_endpoint``,
    ``api_version``, and ``api_key``.

    Attributes:
        deployment_name: The deployment name in Azure OpenAI Studio.
        azure_endpoint: The Azure endpoint URL
            (e.g. ``https://my-resource.openai.azure.com``).
        api_version: Azure API version (e.g. ``2024-02-15-preview``).
        api_key: Azure API key (env: ``AZURE_OPENAI_API_KEY``).
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_API_KEY"))
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_ENDPOINT"))
    deployment_name: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_DEPLOYMENT_NAME"))
    api_version: str = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_API_VERSION")
        or "2024-02-15-preview")
    proxy: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_PROXY"))

    def _build_client_kwargs(self) -> dict:
        """Build kwargs for AzureOpenAI client construction."""
        kwargs = {
            "api_key": self.api_key,
            "azure_endpoint": self.api_base,
            "api_version": self.api_version,
        }
        if self.proxy:
            kwargs["http_client"] = self._build_http_client()
        return kwargs

    def _build_http_client(self):
        """Build an httpx client with proxy support."""
        import httpx
        return httpx.Client(proxies=self.proxy)

    def _new_client(self) -> Any:
        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise ImportError(
                "openai is not installed. Install it with 'pip install openai'."
            ) from exc
        return AzureOpenAI(**self._build_client_kwargs())

    def _new_async_client(self) -> Any:
        try:
            from openai import AsyncAzureOpenAI
        except ImportError as exc:
            raise ImportError(
                "openai is not installed. Install it with 'pip install openai'."
            ) from exc
        kwargs = self._build_client_kwargs()
        return AsyncAzureOpenAI(**kwargs)

    def _call(self, messages: list, **kwargs: Any) \
            -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Synchronous call — uses Azure deployment_name as the model."""
        kwargs.setdefault("model", self.deployment_name or self.model_name)
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) \
            -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronous call — uses Azure deployment_name as the model."""
        kwargs.setdefault("model", self.deployment_name or self.model_name)
        return await super()._acall(messages, **kwargs)

    def max_context_length(self) -> int:
        """Max context length for Azure OpenAI models."""
        return AZURE_OPENAI_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)

    def get_num_tokens(self, text: str) -> int:
        """Estimate token count using tiktoken (cl100k_base fallback)."""
        try:
            import tiktoken
            try:
                encoding = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            return super().get_num_tokens(text)
