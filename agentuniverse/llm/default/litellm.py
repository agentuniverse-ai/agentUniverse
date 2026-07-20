#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/04/24
# @Author  : RheagalFire
# @FileName: litellm.py

from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput


class LiteLLM(LLM):
    """LiteLLM provider — routes to 100+ LLM providers via a unified interface.

    Supports OpenAI, Anthropic, AWS Bedrock, Google Vertex AI, Gemini, Cohere,
    Mistral, Groq, Together AI, Ollama, and more through litellm.completion().

    Provider API keys are read from environment variables automatically
    (OPENAI_API_KEY, ANTHROPIC_API_KEY, AWS_ACCESS_KEY_ID, GEMINI_API_KEY, etc.).

    Model names use LiteLLM format: "provider/model-name", e.g.:
        - openai/gpt-4o
        - anthropic/claude-sonnet-4-20250514
        - bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
        - gemini/gemini-2.5-flash

    See https://docs.litellm.ai/docs/providers for the full list.

    Attributes:
        api_key: Optional API key — only needed for LiteLLM proxy. For direct
            provider access, set the provider's env var instead.
        api_base: Optional base URL — only needed for LiteLLM proxy.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("LITELLM_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("LITELLM_API_BASE"))

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the LiteLLM LLM.

        Args:
            messages: The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        import litellm

        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        completion_kwargs = {
            "model": kwargs.pop("model", self.model_name),
            "messages": messages,
            "temperature": kwargs.pop("temperature", self.temperature),
            "max_tokens": kwargs.pop("max_tokens", self.max_tokens),
            "stream": streaming,
            "drop_params": True,
            **kwargs,
        }
        if self.api_key:
            completion_kwargs["api_key"] = self.api_key
        if self.api_base:
            completion_kwargs["api_base"] = self.api_base

        response = litellm.completion(**completion_kwargs)

        if not streaming:
            text = response.choices[0].message.content
            return LLMOutput(text=text, raw=response.model_dump())
        return self._generate_stream_result(response)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the LiteLLM LLM.

        Args:
            messages: The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        import litellm

        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        completion_kwargs = {
            "model": kwargs.pop("model", self.model_name),
            "messages": messages,
            "temperature": kwargs.pop("temperature", self.temperature),
            "max_tokens": kwargs.pop("max_tokens", self.max_tokens),
            "stream": streaming,
            "drop_params": True,
            **kwargs,
        }
        if self.api_key:
            completion_kwargs["api_key"] = self.api_key
        if self.api_base:
            completion_kwargs["api_base"] = self.api_base

        response = await litellm.acompletion(**completion_kwargs)

        if not streaming:
            text = response.choices[0].message.content
            return LLMOutput(text=text, raw=response.model_dump())
        return self._agenerate_stream_result(response)

    def _generate_stream_result(self, stream) -> Iterator[LLMOutput]:
        """Generate streaming results."""
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", "") or ""
            yield LLMOutput(text=text, raw=chunk.model_dump())

    async def _agenerate_stream_result(self, stream) -> AsyncIterator[LLMOutput]:
        """Generate async streaming results."""
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", "") or ""
            yield LLMOutput(text=text, raw=chunk.model_dump())

    def max_context_length(self) -> int:
        """Return the max context length. Falls back to litellm's model info if available."""
        if self._max_context_length:
            return self._max_context_length
        try:
            import litellm
            info = litellm.get_model_info(self.model_name)
            return info.get("max_input_tokens", 4096)
        except Exception:
            return 4096

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens in the text."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except Exception:
            return len(text) // 4

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> "LiteLLM":
        super().initialize_by_component_configer(component_configer)
        if "api_key" in component_configer.configer.value:
            api_key = component_configer.configer.value.get("api_key")
            self.api_key = process_yaml_func(api_key, component_configer.yaml_func_instance)
        elif "api_key_env" in component_configer.configer.value:
            self.api_key = get_from_env(component_configer.configer.value.get("api_key_env"))
        if "api_base" in component_configer.configer.value:
            api_base = component_configer.configer.value.get("api_base")
            self.api_base = process_yaml_func(api_base, component_configer.yaml_func_instance)
        elif "api_base_env" in component_configer.configer.value:
            self.api_base = get_from_env(component_configer.configer.value.get("api_base_env"))
        return self
