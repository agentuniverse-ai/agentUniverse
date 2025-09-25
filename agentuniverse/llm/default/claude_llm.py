# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 17:49
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: claude_llm.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

import anthropic
import httpx
from langchain_core.language_models import BaseLanguageModel
from pydantic import Field

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.claude_langchain_instance import ClaudeLangChainInstance
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput

ClaudeMAXCONTETNLENGTH = {
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    "claude-2.1": 200000,
    "claude-2.0": 100000,
    "claude-instant-1.2": 100000,
}


class ClaudeLLM(LLM):
    """
    This class implements an interface for interacting with the Anthropic Claude model.

    Attribute:
        api_key (Optional[str]): The API key for the Anthropic API. Defaults to the value of the environment variable ANTHROPIC_API_KEY.
        api_url (Optional[str]): The URL for the Anthropic API. Defaults to the value of the environment variable ANTHROPIC_API_URL.
        proxy (Optional[str]): The proxy to use for the Anthropic API. Defaults to None.
        connection_pool_limits (Optional[int]): The maximum number of connections to keep in a pool. Defaults to None.
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("ANTHROPIC_API_KEY"))
    api_url: Optional[str] = Field(default_factory=lambda: get_from_env("ANTHROPIC_API_URL"))
    proxy: Optional[str] = Field(default_factory=lambda: get_from_env("ANTHROPIC_PROXY"))
    connection_pool_limits: Optional[int] = None

    def _new_client(self):
        client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url=self.api_url,
            timeout=self.request_timeout if self.request_timeout else 60,
            max_retries=self.max_retries if self.max_retries else 2,
            http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,
            connection_pool_limits=self.connection_pool_limits,
        )
        return client

    def _new_async_client(self):
        client = anthropic.AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.api_url,
            timeout=self.request_timeout if self.request_timeout else 60,
            max_retries=self.max_retries if self.max_retries else 2,
            http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
            connection_pool_limits=self.connection_pool_limits,
        )
        return client

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the Claude LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.client = self._new_client()
        chat_completion = self.client.messages.create(
            messages=messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=kwargs.pop("stream", streaming),
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            **kwargs,
        )
        if not streaming:
            self.close()
            return self.parse_result(chat_completion)
        return self.generate_stream_result(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.client = self._new_async_client()
        chat_completion = await self.client.messages.create(
            messages=messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=kwargs.pop("stream", streaming),
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            **kwargs,
        )
        if not streaming:
            await self.aclose()
            return self.parse_result(chat_completion)
        return self.agenerate_stream_result(chat_completion)

    @staticmethod
    def parse_result(data):
        text = data.content[0].text
        if not text:
            return
        return LLMOutput(text=text, raw=data)

    def generate_stream_result(self, chat_completion: Iterator):
        for chunk in chat_completion:
            if chunk.type != "content_block_delta":
                continue
            yield LLMOutput(text=chunk.delta.text, raw=chunk.model_dump())
        self.close()

    async def agenerate_stream_result(self, chat_completion: AsyncIterator):
        async for chunk in chat_completion:
            print(chunk)
            if chunk.type != "content_block_delta":
                continue
            yield LLMOutput(text=chunk.delta.text, raw=chunk.model_dump())
        await self.aclose()

    def as_langchain(self) -> BaseLanguageModel:
        """
        Convert this instance into a LangChain compatible object
        """
        self.init_channel()
        if self._channel_instance:
            return self._channel_instance.as_langchain()
        return ClaudeLangChainInstance(self)

    def get_num_tokens(self, text: str) -> int:
        encode = self._new_client().count_tokens(text)
        return encode

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return ClaudeMAXCONTETNLENGTH[self.model_name]

    def close(self):
        """Close the client."""
        if hasattr(self, "client") and self.client:
            self.client.close()

    async def aclose(self):
        """Async close the client."""
        if hasattr(self, "async_client") and self.async_client:
            await self.async_client.aclose()

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> "ClaudeLLM":
        super().initialize_by_component_configer(component_configer)
        if "api_key" in component_configer.configer.value:
            api_key = component_configer.configer.value.get("api_key")
            self.api_key = process_yaml_func(api_key, component_configer.yaml_func_instance)
        if "api_url" in component_configer.configer.value:
            api_url = component_configer.configer.value.get("api_url")
            self.api_url = process_yaml_func(api_url, component_configer.yaml_func_instance)
        if "proxy" in component_configer.configer.value:
            self.proxy = component_configer.configer.value.get("proxy")
        if "connection_pool_limits" in component_configer.configer.value:
            self.connection_pool_limits = component_configer.configer.value.get("connection_pool_limits")
        return self
