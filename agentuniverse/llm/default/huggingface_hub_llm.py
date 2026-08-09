# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: huggingface_hub_llm.py
import logging
from typing import Any, Optional, Iterator, Union, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput

logger = logging.getLogger(__name__)


class HuggingFaceHubLLM(LLM):
    """LLM component backed by Hugging Face Inference API.

    Supports 100k+ models hosted on the Hugging Face Hub via the
    ``InferenceClient`` from ``huggingface_hub``.

    Attributes:
        model_name: The Hugging Face model repo ID
            (e.g. ``"meta-llama/Meta-Llama-3-8B-Instruct"``).
        api_key: Hugging Face API token (env: ``HUGGINGFACE_API_KEY``
            or ``HF_TOKEN``).
        inference_endpoint: Optional custom inference endpoint URL for
            dedicated endpoints (TEI / TGI).
        timeout: Request timeout in seconds (default 30).
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_API_KEY")
        or get_from_env("HF_TOKEN"))
    inference_endpoint: Optional[str] = Field(
        default_factory=lambda: get_from_env("HUGGINGFACE_INFERENCE_ENDPOINT"))
    timeout: float = 30.0
    client: Any = None
    async_client: Any = None

    def _new_client(self) -> Any:
        try:
            from huggingface_hub import InferenceClient
        except ImportError as exc:
            raise ImportError(
                "huggingface_hub is not installed. Install it with "
                "'pip install huggingface_hub'.") from exc
        self.client = InferenceClient(
            model=self.inference_endpoint or self.model_name,
            token=self.api_key,
            timeout=self.timeout,
        )
        return self.client

    def _new_async_client(self) -> Any:
        try:
            from huggingface_hub import AsyncInferenceClient
        except ImportError as exc:
            raise ImportError(
                "huggingface_hub is not installed. Install it with "
                "'pip install huggingface_hub'.") from exc
        self.async_client = AsyncInferenceClient(
            model=self.inference_endpoint or self.model_name,
            token=self.api_key,
            timeout=self.timeout,
        )
        return self.async_client

    def _ensure_client(self) -> Any:
        if self.client is None:
            self._new_client()
        return self.client

    def _ensure_async_client(self) -> Any:
        if self.async_client is None:
            self._new_async_client()
        return self.async_client

    def _call(self, messages: list, **kwargs: Any) \
            -> Union[LLMOutput, Iterator[LLMOutput]]:
        streaming = kwargs.pop("streaming", self.streaming)
        client = self._ensure_client()

        if streaming:
            def _stream() -> Iterator[LLMOutput]:
                for chunk in client.chat_completion(
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    stream=True,
                ):
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield LLMOutput(text=delta, raw=str(chunk))
            return _stream()
        else:
            response = client.chat_completion(
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                stream=False,
            )
            text = response.choices[0].message.content or ""
            return LLMOutput(text=text, raw=str(response))

    async def _acall(self, messages: list, **kwargs: Any) \
            -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        streaming = kwargs.pop("streaming", self.streaming)
        client = self._ensure_async_client()

        if streaming:
            async def _astream() -> AsyncIterator[LLMOutput]:
                async for chunk in await client.chat_completion(
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    stream=True,
                ):
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield LLMOutput(text=delta, raw=str(chunk))
            return _astream()
        else:
            response = await client.chat_completion(
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                stream=False,
            )
            text = response.choices[0].message.content or ""
            return LLMOutput(text=text, raw=str(response))

    def max_context_length(self) -> int:
        # HF models vary widely; 4096 is a safe default.
        return 4096

    def get_num_tokens(self, text: str) -> int:
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            return len(text) // 4
