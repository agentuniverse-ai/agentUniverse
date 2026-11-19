# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/06
# @FileName: huggingface_hub_llm.py

from typing import Any, Optional, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm import LLM, LLMOutput

try:
    import tiktoken
except ImportError:
    tiktoken = None

HUGGINGFACE_HUB_MAX_CONTEXT_LENGTH = {
    "meta-llama/Llama-3.1-8B-Instruct": 128072,
    "meta-llama/Llama-3.1-70B-Instruct": 128072,
    "meta-llama/Llama-3.2-1B-Instruct": 128072,
    "meta-llama/Llama-3.2-3B-Instruct": 128072,
    "meta-llama/Llama-3.2-11B-Vision-Instruct": 128072,
    "meta-llama/Llama-3.2-90B-Vision-Instruct": 128072,
    "mistralai/Mistral-7B-Instruct-v0.3": 32768,
    "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
    "mistralai/Mistral-Nemo-Instruct-2407": 128000,
    "Qwen/Qwen2.5-7B-Instruct": 32768,
    "Qwen/Qwen2.5-72B-Instruct": 32768,
    "Qwen/Qwen2.5-Coder-32B-Instruct": 32768,
    "google/gemma-2-2b-it": 8192,
    "google/gemma-2-9b-it": 8192,
    "google/gemma-2-27b-it": 8192,
}


def _to_raw(obj: Any) -> Any:
    """Serialize a HuggingFace BaseInferenceType (dict subclass) to a plain dict."""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    if isinstance(obj, dict):
        return dict(obj)
    return str(obj)


class HuggingFaceHubLLM(LLM):
    """HuggingFace Hub LLM component.

    Uses huggingface_hub.InferenceClient to interact with models
    deployed on the HuggingFace Inference API or a dedicated TGI endpoint.

    Attributes:
        api_key: HuggingFace API token (env: HF_TOKEN or HUGGINGFACEHUB_API_TOKEN).
        api_base: Optional custom inference endpoint URL.
        model_name: HuggingFace model id (e.g. meta-llama/Llama-3.2-3B-Instruct).
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("HF_TOKEN")
        or get_from_env("HUGGINGFACEHUB_API_TOKEN")
    )
    api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACEHUB_API_BASE")
    )

    def _build_kwargs(self) -> dict:
        """Build common kwargs for InferenceClient / AsyncInferenceClient."""
        kwargs = {"token": self.api_key, "timeout": self.request_timeout}
        if self.api_base:
            kwargs["url"] = self.api_base
        else:
            kwargs["model"] = self.model_name
        return kwargs

    def _new_client(self):
        """Initialize the HuggingFace InferenceClient."""
        if self.client is not None:
            return self.client
        from huggingface_hub import InferenceClient
        self.client = InferenceClient(**self._build_kwargs())
        return self.client

    def _new_async_client(self):
        """Initialize the async HuggingFace InferenceClient."""
        if self.async_client is not None:
            return self.async_client
        from huggingface_hub import AsyncInferenceClient
        self.async_client = AsyncInferenceClient(**self._build_kwargs())
        return self.async_client

    def _call(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the HuggingFace Hub LLM synchronously.

        Args:
            messages: The messages list (each item is a dict with role/content).
            **kwargs: Additional arguments (streaming, temperature, max_tokens, etc.).
        """
        client = self._new_client()
        streaming = kwargs.pop("streaming", self.streaming)
        temperature = kwargs.pop("temperature", self.temperature)
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        model = kwargs.pop("model", self.model_name)

        if streaming:
            stream = client.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )
            return self._generate_stream_result(stream)
        else:
            response = client.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs,
            )
            text = response.choices[0].message.content
            return LLMOutput(text=text, raw=_to_raw(response))

    async def _acall(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Run the HuggingFace Hub LLM asynchronously.

        Args:
            messages: The messages list (each item is a dict with role/content).
            **kwargs: Additional arguments (streaming, temperature, max_tokens, etc.).
        """
        client = self._new_async_client()
        streaming = kwargs.pop("streaming", self.streaming)
        temperature = kwargs.pop("temperature", self.temperature)
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        model = kwargs.pop("model", self.model_name)

        if streaming:
            stream = await client.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )
            return self._agenerate_stream_result(stream)
        else:
            response = await client.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs,
            )
            text = response.choices[0].message.content
            return LLMOutput(text=text, raw=_to_raw(response))

    def _generate_stream_result(self, stream) -> Iterator[LLMOutput]:
        """Generate LLMOutput from a sync stream."""
        for chunk in stream:
            text = ""
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    text = delta.content
            yield LLMOutput(text=text, raw=_to_raw(chunk))

    async def _agenerate_stream_result(self, stream) -> AsyncIterator[LLMOutput]:
        """Generate LLMOutput from an async stream."""
        async for chunk in stream:
            text = ""
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    text = delta.content
            yield LLMOutput(text=text, raw=_to_raw(chunk))

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Uses tiktoken's cl100k_base encoding as an approximation
        for HuggingFace models that don't have a native tokenizer available.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """
        if tiktoken is None:
            return len(text) // 4
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def max_context_length(self) -> int:
        """Max context length for common HuggingFace Hub models."""
        if super().max_context_length():
            return super().max_context_length()
        return HUGGINGFACE_HUB_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)

    def initialize_by_component_configer(self, component_configer) -> 'LLM':
        """Initialize from config, handling api_base field."""
        super().initialize_by_component_configer(component_configer)
        if component_configer.configer.value.get('api_base'):
            self.api_base = component_configer.configer.value.get('api_base')
        elif component_configer.configer.value.get('api_base_env'):
            self.api_base = get_from_env(
                component_configer.configer.value.get('api_base_env'))
        if component_configer.configer.value.get('api_key'):
            self.api_key = component_configer.configer.value.get('api_key')
        elif component_configer.configer.value.get('api_key_env'):
            self.api_key = get_from_env(
                component_configer.configer.value.get('api_key_env'))
        return self
