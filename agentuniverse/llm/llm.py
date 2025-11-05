# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:04
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm.py
from abc import abstractmethod
from copy import deepcopy
from typing import Optional, Any, AsyncIterator, Iterator, Union

import tiktoken
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.runnables import Runnable

from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_channel.llm_channel_manager import LLMChannelManager
from agentuniverse.llm.llm_output import LLMOutput


class LLM(ComponentBase):
    """The basic class for llm model.

    Attributes:
        client (Any): The client of the llm.
        async_client (Any): The async client of the llm.
        name (Optional[str]): The name of the llm class.
        description (Optional[str]): The description of the llm model.
        model_name (Optional[str]): The name of the llm model, such as gpt-4, gpt-3.5-turbo.
        temperature (Optional[float]): The temperature of the llm model,
        what sampling temperature to use, between 0 and 2.
        request_timeout (Optional[int]): The request timeout for chat http requests.
        max_tokens (Optional[int]): The maximum number of [tokens](/tokenizer) that can be generated in the completion.
        streaming (Optional[bool]): Whether to stream the results or not.
        ext_info (Optional[dict]): The extended information of the llm model.
    """

    class Config:
        arbitrary_types_allowed = True

    client: Any = None
    async_client: Any = None
    name: Optional[str] = None
    description: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = 0.5
    request_timeout: Optional[int] = None
    max_tokens: Optional[int] = 1024
    max_retries: Optional[int] = 2
    streaming: Optional[bool] = False
    ext_info: Optional[dict] = None
    tracing: Optional[bool] = None
    _max_context_length: Optional[int] = None
    langchain_instance: Optional[BaseLanguageModel] = None
    channel: Optional[str] = None
    _channel_instance: Optional[LLMChannel] = None

    def __init__(self, **kwargs):
        """Initialize the llm."""
        super().__init__(component_type=ComponentEnum.LLM, **kwargs)

    def init_channel(self):
        if self.channel and not self._channel_instance:
            llm_channel: LLMChannel = LLMChannelManager().get_instance_obj(
                component_instance_name=self.channel)
            if not llm_channel:
                return

            self._channel_instance = llm_channel

            llm_attrs = vars(self)
            channel_model_config = {}

            for attr_name, attr_value in llm_attrs.items():
                channel_model_config[attr_name] = attr_value

            llm_channel.channel_model_config = channel_model_config

    def _new_client(self):
        """Initialize the client."""
        pass

    def _new_async_client(self):
        """Initialize the async client."""
        pass

    @abstractmethod
    def _call(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the LLM."""

    @abstractmethod
    async def _acall(self, *args: Any, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the LLM."""

    def as_langchain(self) -> BaseLanguageModel:
        """Convert to the langchain llm class."""
        self.init_channel()
        if self._channel_instance:
            return self._channel_instance.as_langchain()
        pass

    def get_instance_code(self) -> str:
        """Return the full name of the llm."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LLM':
        """Initialize the LLM by the ComponentConfiger object.

        Args:
            component_configer(LLMConfiger): the ComponentConfiger object
        Returns:
            LLM: the LLM object
        """
        super().initialize_by_component_configer(component_configer)
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if component_configer.model_name:
            self.model_name = component_configer.model_name
        if component_configer.temperature:
            self.temperature = component_configer.temperature
        if component_configer.request_timeout:
            self.request_timeout = component_configer.request_timeout
        if component_configer.max_tokens:
            self.max_tokens = component_configer.max_tokens
        if component_configer.max_retries:
            self.max_retries = component_configer.max_retries
        if component_configer.streaming:
            self.streaming = component_configer.streaming
        if component_configer.ext_info:
            self.ext_info = component_configer.ext_info
        self.tracing = component_configer.tracing
        if 'max_context_length' in component_configer.configer.value:
            self._max_context_length = component_configer.configer.value['max_context_length']
        if 'channel' in component_configer.configer.value:
            self.channel = component_configer.configer.value.get('channel')
        return self

    def set_by_agent_model(self, **kwargs):
        """ Assign values of parameters to the LLM model in the agent configuration."""
        # note: default shallow copy
        copied_obj = self.model_copy()
        if 'model_name' in kwargs and kwargs['model_name']:
            copied_obj.model_name = kwargs['model_name']
        if 'temperature' in kwargs and kwargs['temperature']:
            copied_obj.temperature = kwargs['temperature']
        if 'request_timeout' in kwargs and kwargs['request_timeout']:
            copied_obj.request_timeout = kwargs['request_timeout']
        if 'max_tokens' in kwargs and kwargs['max_tokens']:
            copied_obj.max_tokens = kwargs['max_tokens']
        if 'max_retries' in kwargs and kwargs['max_retries']:
            copied_obj.max_retries = kwargs['max_retries']
        if 'streaming' in kwargs and kwargs['streaming']:
            copied_obj.streaming = kwargs['streaming']
        if 'max_context_length' in kwargs and kwargs['max_context_length']:
            copied_obj._max_context_length = kwargs['max_context_length']
        return copied_obj

    def max_context_length(self) -> int:
        """Max context length.

        The total length of input tokens and generated tokens is limited by the model's context length.
        """
        return self._max_context_length

    @abstractmethod
    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in a model's context window.

        Args:
            text: The string input to tokenize.
            model: The model you want to calculate


        Returns:
            The integer number of tokens in the text.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def as_langchain_runnable(self, params=None) -> Runnable:
        """Get the langchain llm class."""
        if params is None:
            params = {}
        return self.as_langchain().bind(**params)

    @trace_llm
    def call(self, *args: Any, **kwargs: Any):
        """Run the LLM."""
        try:
            self.init_channel()
            if self._channel_instance:
                return self._channel_instance._call(*args, **kwargs)
            return self._call(*args, **kwargs)
        except Exception as e:
            LOGGER.error(f'Error in LLM call: {e}')
            raise e

    @trace_llm
    async def acall(self, *args: Any, **kwargs: Any):
        """Asynchronously run the LLM."""
        try:
            self.init_channel()
            if self._channel_instance:
                return await self._channel_instance._acall(*args, **kwargs)
            return await self._acall(*args, **kwargs)
        except Exception as e:
            LOGGER.error(f'Error in LLM acall: {e}')
            raise e

    def create_copy(self):
        copied = self.model_copy()
        if self.ext_info is not None:
            copied.ext_info = deepcopy(self.ext_info)
        # Shared reference
        copied.client = self.client
        copied.async_client = self.async_client
        copied.langchain_instance = self.langchain_instance
        return copied
