# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/16 15:28
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_channel.py
from typing import Optional, Any, Union, Iterator, AsyncIterator

import httpx
import openai
import tiktoken
from openai import OpenAI, AsyncOpenAI
from langchain_core.language_models import BaseLanguageModel

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.llm.llm_channel.langchain_instance.default_channel_langchain_instance import \
    DefaultChannelLangchainInstance
from agentuniverse.llm.llm_output import LLMOutput, TokenUsage


class LLMChannel(ComponentBase):
    channel_name: Optional[str] = None
    channel_api_key: Optional[str] = None
    channel_api_base: Optional[str] = None
    channel_organization: Optional[str] = None
    channel_proxy: Optional[str] = None
    channel_model_name: Optional[str] = None
    channel_ext_info: Optional[dict] = None
    ext_headers: Optional[dict] = {}
    ext_params: Optional[dict] = {}

    model_support_stream: Optional[bool] = None
    model_support_max_context_length: Optional[int] = None
    model_support_max_tokens: Optional[int] = None
    model_is_openai_protocol_compatible: Optional[bool] = True

    _channel_model_config: Optional[dict] = None
    client: Any = None
    async_client: Any = None
    component_type: ComponentEnum = ComponentEnum.LLM_CHANNEL

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'LLMChannel':

        super()._initialize_by_component_configer(component_configer)
        if hasattr(component_configer, "channel_name"):
            self.channel_name = component_configer.channel_name
        if hasattr(component_configer, "channel_api_key"):
            self.channel_api_key = component_configer.channel_api_key
        if hasattr(component_configer, "channel_api_base"):
            self.channel_api_base = component_configer.channel_api_base
        if hasattr(component_configer, "channel_organization"):
            self.channel_organization = component_configer.channel_organization
        if hasattr(component_configer, "channel_proxy"):
            self.channel_proxy = component_configer.channel_proxy
        if hasattr(component_configer, "channel_model_name"):
            self.channel_model_name = component_configer.channel_model_name
        if hasattr(component_configer, "channel_ext_info"):
            self.channel_ext_info = component_configer.channel_ext_info
        if hasattr(component_configer, "model_support_stream"):
            self.model_support_stream = component_configer.model_support_stream
        if hasattr(component_configer, "model_support_max_context_length"):
            self.model_support_max_context_length = component_configer.model_support_max_context_length
        if hasattr(component_configer, "model_support_max_tokens"):
            self.model_support_max_tokens = component_configer.model_support_max_tokens
        if hasattr(component_configer, "model_is_openai_protocol_compatible"):
            self.model_is_openai_protocol_compatible = component_configer.model_is_openai_protocol_compatible
        if component_configer.configer.value.get("extra_headers"):
            self.ext_headers = component_configer.configer.value.get("extra_headers", {})
        if component_configer.configer.value.get("extra_params"):
            self.ext_params = component_configer.configer.value.get("extra_params", {})
            self.ext_params["stream_options"] = {
                "include_usage": True
            }
        else:
            self.ext_params = {
                "stream_options": {
                    "include_usage": True
                }
            }
        return self

    def create_copy(self):
        return self

    @property
    def channel_model_config(self):
        return self._channel_model_config

    @channel_model_config.setter
    def channel_model_config(self, config: dict):
        self._channel_model_config = config
        if config:
            for key, value in config.items():
                if not isinstance(key, str):
                    continue
                if key == 'streaming':
                    if self.model_support_stream is False:
                        value = False
                if key == 'max_tokens':
                    if self.model_support_max_tokens:
                        value = min(self.model_support_max_tokens, value) if value else self.model_support_max_tokens
                if key == 'max_context_length':
                    if self.model_support_max_context_length:
                        value = min(self.model_support_max_context_length,
                                    value) if value else self.model_support_max_context_length
                if key == 'ext_params' and value and isinstance(value, dict):
                    self.ext_params.update(value)
                if key == 'ext_headers' and value and isinstance(value, dict):
                    self.ext_headers.update(value)
                if not self.__dict__.get(key):
                    self.__dict__[key] = value

    @trace_llm
    def call(self, *args: Any, **kwargs: Any):
        """Run the LLM."""
        return self._call(*args, **kwargs)

    @trace_llm
    async def acall(self, *args: Any, **kwargs: Any):
        """Asynchronously run the LLM."""
        return await self._acall(*args, **kwargs)

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.channel_model_config.get('streaming')
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        if self.model_support_stream is False and streaming is True:
            streaming = False
        support_max_tokens = self.model_support_max_tokens
        max_tokens = kwargs.pop('max_tokens', None) or self.channel_model_config.get('max_tokens',
                                                                                     None) or support_max_tokens
        if support_max_tokens:
            max_tokens = min(support_max_tokens, max_tokens)

        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop("extra_body", {})
        ext_params = {**ext_params, **extra_body}
        if not streaming:
            ext_params.pop("stream_options", None)
        self.client = self._new_client()
        self.client.base_url = kwargs.pop('api_base') if kwargs.get('api_base') else self.channel_api_base
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.channel_model_name),
            temperature=kwargs.pop('temperature', self.channel_model_config.get('temperature')),
            stream=kwargs.pop('stream', streaming),
            max_tokens=max_tokens,
            extra_body=ext_params,
            extra_headers=kwargs.pop("extra_headers", self.ext_headers),
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump(),
                             message=Message(content=chat_completion.choices[0].message.content,
                                             type=chat_completion.choices[0].message.role))
        return self.generate_stream_result(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.channel_model_config.get('streaming')
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        if self.model_support_stream is False and streaming is True:
            streaming = False

        support_max_tokens = self.model_support_max_tokens
        max_tokens = kwargs.pop('max_tokens', None) or self.channel_model_config.get('max_tokens',
                                                                                     None) or support_max_tokens
        if support_max_tokens:
            max_tokens = min(support_max_tokens, max_tokens)
        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop("extra_body", {})
        ext_params = {**ext_params, **extra_body}
        if not streaming:
            ext_params.pop("stream_options", None)
        self.async_client = self._new_async_client()
        self.async_client.base_url = kwargs.pop('api_base') if kwargs.get('api_base') else self.channel_api_base
        chat_completion = await self.async_client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.channel_model_name),
            temperature=kwargs.pop('temperature', self.channel_model_config.get('temperature')),
            stream=kwargs.pop('stream', streaming),
            max_tokens=max_tokens,
            extra_headers=kwargs.pop("extra_headers", self.ext_headers),
            extra_body=ext_params,
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump(),
                             message=Message(content=chat_completion.choices[0].message.content,
                                             type=chat_completion.choices[0].message.role))
        return self.agenerate_stream_result(chat_completion)

    def as_langchain(self) -> BaseLanguageModel:
        """Convert to the langchain llm class."""
        return DefaultChannelLangchainInstance(self)

    def get_num_tokens(self, text: str, model=None) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def max_context_length(self) -> int:
        return self.channel_model_config.get('max_context_length')

    def _new_client(self):
        """Initialize the openai client."""
        if self.client is not None:
            return self.client
        return OpenAI(
            api_key=self.channel_api_key,
            organization=self.channel_organization,
            base_url=self.channel_api_base,
            timeout=self.channel_model_config.get('request_timeout'),
            max_retries=self.channel_model_config.get('max_retries'),
            http_client=httpx.Client(proxy=self.channel_proxy) if self.channel_proxy else None,
            **(self.channel_model_config.get('client_args') or {}),
        )

    def _new_async_client(self):
        """Initialize the openai async client."""
        if self.async_client is not None:
            return self.async_client
        return AsyncOpenAI(
            api_key=self.channel_api_key,
            organization=self.channel_organization,
            base_url=self.channel_api_base,
            timeout=self.channel_model_config.get('request_timeout'),
            max_retries=self.channel_model_config.get('max_retries'),
            http_client=httpx.AsyncClient(proxy=self.channel_proxy) if self.channel_proxy else None,
            **(self.channel_model_config.get('client_args') or {}),
        )

    def generate_stream_result(self, stream: openai.Stream):
        """Generate the result of the stream."""
        for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output

    async def agenerate_stream_result(self, stream: AsyncIterator) -> AsyncIterator[LLMOutput]:
        """Generate the result of the stream."""
        async for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output

    @staticmethod
    def parse_result(chunk):
        """Generate the result of the stream."""
        chat_completion = chunk
        if not isinstance(chunk, dict):
            chunk = chunk.model_dump()

        if len(chunk["choices"]) == 0:
            return LLMOutput(text="", raw=chunk,
                             usage=TokenUsage.from_openai(chunk.get('usage', {})))
        choice = chunk["choices"][0]
        message = choice.get("delta")
        text = message.get("content")
        role = message.get("role")
        if text is None:
            text = ""
        return LLMOutput(
            text=text,
            raw=chat_completion.model_dump(),
            message=Message(content=text, type=role),
            usage=TokenUsage.from_openai(chunk.get('usage', {}))
        )

    def get_instance_code(self) -> str:
        """Return the full name of the component."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.channel_name}'
