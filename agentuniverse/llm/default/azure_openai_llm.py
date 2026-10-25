# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/25 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: azure_openai_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM
from agentuniverse.llm.llm_output import LLMOutput


class AzureOpenAILLM(OpenAIStyleLLM):
    """
    Azure OpenAI LLM implementation.

    Attributes:
        api_key (Optional[str]): The Azure OpenAI API key.
        api_base (Optional[str]): The Azure OpenAI endpoint URL.
        api_version (Optional[str]): The Azure OpenAI API version.
        deployment_name (Optional[str]): The Azure OpenAI deployment name.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_OPENAI_API_KEY"))
    api_base: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_OPENAI_ENDPOINT"))
    api_version: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_OPENAI_API_VERSION") or "2024-02-15-preview")
    deployment_name: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_OPENAI_DEPLOYMENT_NAME"))

    def _new_client(self):
        """Initialize the Azure OpenAI client."""
        from openai import AzureOpenAI

        if self.client is not None:
            return self.client

        return AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
        )

    def _new_async_client(self):
        """Initialize the Azure OpenAI async client."""
        from openai import AsyncAzureOpenAI

        if self.async_client is not None:
            return self.async_client

        return AsyncAzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
        )

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Call the Azure OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Union[LLMOutput, Iterator[LLMOutput]]: The LLM output.
        """
        streaming = kwargs.pop("streaming", self.streaming)
        self.client = self._new_client()

        # Use deployment_name as model if not specified
        model = kwargs.pop('model', self.deployment_name or self.model_name)

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            **kwargs,
        )

        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.generate_stream_result(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Async call the Azure OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Union[LLMOutput, AsyncIterator[LLMOutput]]: The LLM output.
        """
        streaming = kwargs.pop("streaming", self.streaming)
        self.async_client = self._new_async_client()

        # Use deployment_name as model if not specified
        model = kwargs.pop('model', self.deployment_name or self.model_name)

        chat_completion = await self.async_client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            **kwargs,
        )

        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.agenerate_stream_result(chat_completion)

    def max_context_length(self) -> int:
        """Return the maximum context length for the model."""
        if super().max_context_length():
            return super().max_context_length()
        # Default Azure OpenAI context lengths
        azure_context_lengths = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "gpt-35-turbo": 4096,
            "gpt-35-turbo-16k": 16384,
        }
        return azure_context_lengths.get(self.model_name, 4096)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens in the text.

        Args:
            text (str): The text to tokenize.

        Returns:
            int: The number of tokens.
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model_name or "gpt-35-turbo")
            return len(encoding.encode(text))
        except Exception:
            # Fallback estimation
            return len(text.split()) * 2

    def as_langchain(self):
        """Convert to a LangChain compatible LLM."""
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError:
            raise ImportError(
                "langchain_openai is not installed. "
                "Please install it with `pip install langchain-openai`"
            )

        return AzureChatOpenAI(
            azure_endpoint=self.api_base,
            api_key=self.api_key,
            api_version=self.api_version,
            deployment_name=self.deployment_name or self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
