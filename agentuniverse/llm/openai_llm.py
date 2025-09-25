# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:15
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_llm.py
from typing import Any, Optional, AsyncIterator, Iterator, Union

import httpx
from langchain_core.language_models.base import BaseLanguageModel
from openai import OpenAI, AsyncOpenAI
from pydantic import Field
import tiktoken

from agentuniverse.llm.langchain_instance import LangchainOpenAI
from agentuniverse.llm.llm import LLM, LLMOutput
from agentuniverse.base.util.env_util import get_from_env

OPENAI_MAX_CONTEXT_LENGTH = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-3.5-turbo-0125": 16384,
    "gpt-4-0314": 8192,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
}


class OpenAILLM(LLM):
    """The openai llm class.

    Attributes:
        openai_api_key (Optional[str], optional): The API key for the OpenAI API.
        This automatically infers the `openai_api_key` from the environment variable `OPENAI_API_KEY` if not provided.

        openai_organization (Optional[str], optional): The OpenAI organization.
        This automatically infers the `openai_organization` from the environment variable `OPENAI_ORGANIZATION` if not provided.

        openai_api_base (Optional[str], optional): The OpenAI base url.
        This automatically infers the `openai_api_base` from the environment variable `OPENAI_API_BASE` if not provided.

        openai_client_args (Optional[dict], optional): Additional arguments to pass to the OpenAI client.
    """

    openai_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_KEY"))
    openai_organization: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_ORGANIZATION"))
    openai_api_base: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_BASE"))
    openai_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_PROXY"))
    openai_client_args: Optional[dict] = None

    def _new_client(self):
        """Initialize the openai client."""
        return OpenAI(
            api_key=self.openai_api_key,
            organization=self.openai_organization,
            base_url=self.openai_api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.openai_proxy) if self.openai_proxy else None,
            **(self.openai_client_args or {}),
        )

    def _new_async_client(self):
        """Initialize the openai async client."""
        return AsyncOpenAI(
            api_key=self.openai_api_key,
            organization=self.openai_organization,
            base_url=self.openai_api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.openai_proxy) if self.openai_proxy else None,
            **(self.openai_client_args or {}),
        )

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.client = self._new_client()
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=kwargs.pop("stream", streaming),
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.generate_stream_result(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.async_client = self._new_async_client()
        chat_completion = await self.async_client.chat.completions.create(
            messages=messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=kwargs.pop("stream", streaming),
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.agenerate_stream_result(chat_completion)

    def as_langchain(self) -> BaseLanguageModel:
        """Convert the agentUniverse(aU) openai llm class to the langchain openai llm class."""
        return LangchainOpenAI(self)

    def set_by_agent_model(self, **kwargs):
        """Assign values of parameters to the OpenAILLM model in the agent configuration."""
        copied_obj = super().set_by_agent_model(**kwargs)
        if "openai_api_key" in kwargs and kwargs["openai_api_key"]:
            copied_obj.openai_api_key = kwargs["openai_api_key"]
        if "openai_api_base" in kwargs and kwargs["openai_api_base"]:
            copied_obj.openai_api_base = kwargs["openai_api_base"]
        if "openai_proxy" in kwargs and kwargs["openai_proxy"]:
            copied_obj.openai_proxy = kwargs["openai_proxy"]
        if "openai_client_args" in kwargs and kwargs["openai_client_args"]:
            copied_obj.openai_client_args = kwargs["openai_client_args"]
        return copied_obj

    def max_context_length(self) -> int:
        """Max context length.

        The total length of input tokens and generated tokens is limited by the openai model's context length.
        """
        return OPENAI_MAX_CONTEXT_LENGTH.get(self.model_name, 4096)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    @staticmethod
    def parse_result(chunk):
        """Generate the result of the stream."""
        chat_completion = chunk
        if not isinstance(chunk, dict):
            chunk = chunk.dict()
        if len(chunk["choices"]) == 0:
            return
        choice = chunk["choices"][0]
        message = choice.get("delta")
        text = message.get("content")
        if not text:
            return
        return LLMOutput(text=text, raw=chat_completion.model_dump())

    @classmethod
    def generate_stream_result(cls, stream: Iterator) -> Iterator[LLMOutput]:
        """Generate the result of the stream."""
        for chunk in stream:
            llm_output = cls.parse_result(chunk)
            if llm_output:
                yield llm_output

    @classmethod
    async def agenerate_stream_result(cls, stream: AsyncIterator) -> AsyncIterator[LLMOutput]:
        """Generate the result of the stream."""
        async for chunk in stream:
            llm_output = cls.parse_result(chunk)
            if llm_output:
                yield llm_output
