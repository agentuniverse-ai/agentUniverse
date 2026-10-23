#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: azure_openai_llm.py

"""
Azure OpenAI LLM implementation.

This module provides integration with the Azure OpenAI service through the
`openai` SDK's dedicated Azure clients (`AzureOpenAI` / `AsyncAzureOpenAI`).
Compared with pointing a plain `OpenAIStyleLLM` at an Azure endpoint, this
component takes care of the Azure specifics:

- authentication with an Azure resource key (`api-key` header)
- the `api-version` query parameter required by every request
- deployment based routing (`/openai/deployments/{deployment}/...`), so the
  `model_name` used in requests is the deployment name you created in the
    Azure portal rather than the upstream model id

For more information, visit:
https://learn.microsoft.com/azure/ai-services/openai/
"""

from typing import Any, AsyncIterator, Iterator, Optional, Union

import httpx
from openai import AzureOpenAI, AsyncAzureOpenAI
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

# Common Azure OpenAI deployment context lengths.
# Note: these are typical values for the underlying models; the effective
# limit always depends on how the deployment was configured in Azure.
AZURE_OPENAI_MAX_CONTEXT_LENGTH = {
    # GPT-4o family
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4o-2024-05-13": 128000,
    "gpt-4o-2024-08-06": 128000,
    "gpt-4o-mini-2024-07-18": 128000,
    # GPT-4 Turbo
    "gpt-4-turbo": 128000,
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-4-1106-preview": 128000,
    # GPT-4
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-32k-0613": 32768,
    # GPT-3.5 Turbo
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
    "gpt-35-turbo-1106": 16384,
    # o-series reasoning models
    "o1": 200000,
    "o1-mini": 128000,
    "o1-preview": 128000,
    "o3-mini": 200000,
    # Default fallback
    "default": 8192,
}


class AzureOpenAIStyleLLM(OpenAIStyleLLM):
    """Azure OpenAI LLM using the `openai` SDK's Azure clients.

    The `api_base` attribute holds the Azure resource endpoint, e.g.
    `https://your-resource.openai.azure.com/`. `model_name` (or the optional
    `azure_deployment` attribute) holds the deployment name created in the
    Azure portal.

    Configuration Example:
        ```yaml
        name: 'azure_gpt_4o'
        description: 'default azure openai llm'
        model_name: 'gpt-4o'            # deployment name in Azure
        api_base: 'https://your-resource.openai.azure.com/'
        api_key_env: 'AZURE_OPENAI_API_KEY'
        api_version: '2024-08-01-preview'
        max_tokens: 1024
        metadata:
          type: 'LLM'
          module: 'agentuniverse.llm.default.azure_openai_llm'
          class: 'AzureOpenAIStyleLLM'
        ```

    Attributes:
        api_base (Optional[str]): The Azure resource endpoint.
        api_key (Optional[str]): The Azure resource key.
        api_version (Optional[str]): The Azure API version query parameter,
            e.g. `2024-08-01-preview`.
        azure_deployment (Optional[str]): The Azure deployment name; falls
            back to `model_name` when not set.
        organization (Optional[str]): The organization ID to use for requests.
        proxy (Optional[str]): The proxy to use for the API requests.
        client_args (Optional[dict]): Additional arguments for the clients.

    Environment Variables:
        AZURE_OPENAI_ENDPOINT: The Azure resource endpoint.
        AZURE_OPENAI_API_KEY: The Azure resource key.
        AZURE_OPENAI_API_VERSION: The Azure API version.
        AZURE_OPENAI_DEPLOYMENT: The Azure deployment name.
    """

    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_ENDPOINT")
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_API_KEY")
    )
    api_version: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_API_VERSION")
    )
    azure_deployment: Optional[str] = Field(
        default_factory=lambda: get_from_env("AZURE_OPENAI_DEPLOYMENT")
    )

    def deployment_name(self) -> Optional[str]:
        """Return the Azure deployment name used for requests.

        Returns:
            The `azure_deployment` attribute when set, otherwise `model_name`.
        """
        return self.azure_deployment or self.model_name

    def _new_client(self):
        """Initialize the Azure OpenAI client."""
        if self.client is not None:
            return self.client
        return AzureOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            azure_endpoint=self.api_base,
            azure_deployment=self.deployment_name(),
            api_version=self.api_version,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def _new_async_client(self):
        """Initialize the Azure OpenAI async client."""
        if self.async_client is not None:
            return self.async_client
        return AsyncAzureOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            azure_endpoint=self.api_base,
            azure_deployment=self.deployment_name(),
            api_version=self.api_version,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the Azure OpenAI LLM.

        Unlike the plain OpenAI flow, the client `base_url` is never
        overwritten here: the Azure clients derive the request path from the
        endpoint, deployment and api version, and a manual `base_url`
        assignment would drop the `/openai` path segment.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The LLM output, or an iterator of outputs when streaming.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        # an api_base kwarg cannot be applied to an already built azure client
        kwargs.pop('api_base', None)
        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop("extra_body", {})
        ext_params = {**ext_params, **extra_body}
        if streaming and "stream_options" not in ext_params:
            ext_params["stream_options"] = {
                "include_usage": True
            }
        self.client = self._new_client()
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.deployment_name()),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=streaming,
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            extra_headers=kwargs.pop("extra_headers", self.ext_headers),
            extra_body=ext_params,
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.generate_stream_result(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the Azure OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The LLM output, or an async iterator of outputs when streaming.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        kwargs.pop('api_base', None)
        self.async_client: AsyncAzureOpenAI = self._new_async_client()
        async_client = self.async_client
        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop("extra_body", {})
        ext_params = {**ext_params, **extra_body}
        if streaming and "stream_options" not in ext_params:
            ext_params["stream_options"] = {
                "include_usage": True
            }
        chat_completion = await async_client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.deployment_name()),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=streaming,
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            extra_headers=kwargs.pop("extra_headers", self.ext_headers),
            extra_body=ext_params,
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.agenerate_stream_result(chat_completion)

    def set_by_agent_model(self, **kwargs) -> None:
        """Assign values of parameters to the Azure OpenAI LLM in the agent configuration."""
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'api_version' in kwargs and kwargs['api_version']:
            copied_obj.api_version = kwargs['api_version']
        if 'azure_deployment' in kwargs and kwargs['azure_deployment']:
            copied_obj.azure_deployment = kwargs['azure_deployment']
        return copied_obj

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LLM':
        """Initialize the LLM by the component configer.

        Besides the attributes handled by the parent class, the Azure
        specific `api_version` and `azure_deployment` attributes are read
        from the component configuration.
        """
        if 'api_version' in component_configer.configer.value:
            self.api_version = process_yaml_func(
                component_configer.configer.value.get('api_version'),
                component_configer.yaml_func_instance)
        elif 'api_version_env' in component_configer.configer.value:
            self.api_version = get_from_env(component_configer.configer.value.get('api_version_env'))
        if 'azure_deployment' in component_configer.configer.value:
            self.azure_deployment = process_yaml_func(
                component_configer.configer.value.get('azure_deployment'),
                component_configer.yaml_func_instance)
        elif 'azure_deployment_env' in component_configer.configer.value:
            self.azure_deployment = get_from_env(component_configer.configer.value.get('azure_deployment_env'))
        return super().initialize_by_component_configer(component_configer)

    def max_context_length(self) -> int:
        """Return the maximum length of the context.

        Returns:
            The maximum context length in tokens, resolved from the
            `max_context_length` configuration when present, otherwise from
            the deployment name lookup table with an 8192 fallback.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in AZURE_OPENAI_MAX_CONTEXT_LENGTH:
            return AZURE_OPENAI_MAX_CONTEXT_LENGTH[self.model_name]
        return AZURE_OPENAI_MAX_CONTEXT_LENGTH["default"]
