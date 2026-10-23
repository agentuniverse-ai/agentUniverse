#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/15
# @Author  : dxz0069
# @FileName: huggingface_hub_llm.py

"""
Hugging Face Hub LLM implementation.

This module provides integration with the Hugging Face Hub through the
OpenAI-compatible endpoint of the Inference Providers router
(`https://router.huggingface.co/v1`). With a single Hugging Face token it
reaches every provider that serves a given Hub model (together, fireworks,
cerebras, ...), and it also works unchanged against dedicated
Inference Endpoints by overriding `api_base`.

Because the router speaks the OpenAI chat completions protocol, this
component builds on `OpenAIStyleLLM` and adds:

- default endpoint and credential resolution from Hugging Face environment
  variables (`HF_TOKEN` / `HUGGINGFACEHUB_API_TOKEN`)
- optional `provider` routing: when set, requests use the
  `{model_name}:{provider}` form expected by the router

For more information, visit:
https://huggingface.co/docs/inference-providers/
"""

from typing import Union, Iterator, AsyncIterator, Any

from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

HUGGINGFACE_ROUTER_API_BASE = "https://router.huggingface.co/v1"

# Common Hugging Face Hub model context lengths.
# Note: these are typical values for the underlying models; the effective
# limit depends on the serving provider chosen by the router.
HUGGINGFACE_HUB_MAX_CONTEXT_LENGTH = {
    # Meta Llama
    "meta-llama/Llama-3.1-8B-Instruct": 131072,
    "meta-llama/Llama-3.1-70B-Instruct": 131072,
    "meta-llama/Llama-3.1-405B-Instruct": 131072,
    "meta-llama/Llama-3.3-70B-Instruct": 131072,
    "meta-llama/Meta-Llama-3-8B-Instruct": 8192,
    "meta-llama/Meta-Llama-3-70B-Instruct": 8192,
    # Qwen
    "Qwen/Qwen2.5-7B-Instruct": 32768,
    "Qwen/Qwen2.5-72B-Instruct": 32768,
    "Qwen/Qwen2.5-Math-7B-Instruct": 4096,
    "Qwen/Qwen3-32B": 131072,
    # Mistral
    "mistralai/Mistral-7B-Instruct-v0.3": 32768,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
    "mistralai/Mistral-Small-24B-Instruct-2501": 32768,
    # DeepSeek
    "deepseek-ai/DeepSeek-R1": 131072,
    "deepseek-ai/DeepSeek-V3": 131072,
    "deepseek-ai/deepseek-llm-7b-chat": 4096,
    # Others
    "microsoft/Phi-3-medium-4k-instruct": 4096,
    "microsoft/Phi-4": 16384,
    "01-ai/Yi-1.5-34B-Chat": 32768,
    # Default fallback
    "default": 8192,
}


class HuggingFaceHubLLM(OpenAIStyleLLM):
    """Hugging Face Hub LLM via the Inference Providers OpenAI-compatible endpoint.

    Configuration Example:
        ```yaml
        name: 'huggingface_llama'
        description: 'llama 3.1 served through hugging face inference providers'
        model_name: 'meta-llama/Llama-3.1-8B-Instruct'
        provider: 'together'          # optional, routing hint for the router
        api_key_env: 'HF_TOKEN'
        max_tokens: 2048
        metadata:
          type: 'LLM'
          module: 'agentuniverse.llm.default.huggingface_hub_llm'
          class: 'HuggingFaceHubLLM'
        ```

    Attributes:
        api_base (Optional[str]): The OpenAI-compatible endpoint; defaults to
            the Hugging Face Inference Providers router.
        api_key (Optional[str]): The Hugging Face token.
        provider (Optional[str]): The inference provider routing hint, e.g.
            `together`, `fireworks`, `cerebras`. When set and `model_name`
            carries no explicit `:provider` suffix, requests are issued with
            `{model_name}:{provider}`.

    Environment Variables:
        HF_TOKEN or HUGGINGFACEHUB_API_TOKEN: The Hugging Face token.
        HF_API_BASE: A custom OpenAI-compatible endpoint, e.g. a dedicated
            Inference Endpoint like `https://xxx.endpoints.huggingface.cloud/v1`.
    """

    api_base: str = Field(
        default_factory=lambda: get_from_env("HF_API_BASE") or HUGGINGFACE_ROUTER_API_BASE
    )
    api_key: str = Field(
        default_factory=lambda: get_from_env("HF_TOKEN") or get_from_env("HUGGINGFACEHUB_API_TOKEN")
    )
    provider: str = None

    def request_model_name(self) -> str:
        """Return the model identifier sent to the router.

        Returns:
            `{model_name}:{provider}` when a provider is configured and
            `model_name` has no explicit provider suffix, otherwise
            `model_name` unchanged.
        """
        if self.provider and self.model_name and ':' not in self.model_name:
            return f'{self.model_name}:{self.provider}'
        return self.model_name

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the Hugging Face Hub LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The LLM output, or an iterator of outputs when streaming.
        """
        kwargs.setdefault('model', self.request_model_name())
        return super()._call(messages, **kwargs)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the Hugging Face Hub LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The LLM output, or an async iterator of outputs when streaming.
        """
        kwargs.setdefault('model', self.request_model_name())
        return await super()._acall(messages, **kwargs)

    def set_by_agent_model(self, **kwargs) -> None:
        """Assign values of parameters to the Hugging Face Hub LLM in the agent configuration."""
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'provider' in kwargs and kwargs['provider']:
            copied_obj.provider = kwargs['provider']
        return copied_obj

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LLM':
        """Initialize the LLM by the component configer.

        Besides the attributes handled by the parent class, the provider
        routing hint is read from the component configuration.
        """
        if 'provider' in component_configer.configer.value:
            self.provider = process_yaml_func(
                component_configer.configer.value.get('provider'),
                component_configer.yaml_func_instance)
        elif 'provider_env' in component_configer.configer.value:
            self.provider = get_from_env(component_configer.configer.value.get('provider_env'))
        return super().initialize_by_component_configer(component_configer)

    def max_context_length(self) -> int:
        """Return the maximum length of the context.

        Returns:
            The maximum context length in tokens, resolved from the
            `max_context_length` configuration when present, otherwise from
            the model lookup table with an 8192 fallback.
        """
        if self._max_context_length:
            return self._max_context_length
        if self.model_name in HUGGINGFACE_HUB_MAX_CONTEXT_LENGTH:
            return HUGGINGFACE_HUB_MAX_CONTEXT_LENGTH[self.model_name]
        return HUGGINGFACE_HUB_MAX_CONTEXT_LENGTH["default"]
