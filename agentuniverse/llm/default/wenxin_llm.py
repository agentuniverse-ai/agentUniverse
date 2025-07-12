# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: wenxin_llm.py
from typing import Any, Union, AsyncIterator, Iterator

import qianfan
from langchain_core.language_models import BaseLanguageModel
from pydantic import Field
from qianfan import QfResponse
from qianfan.resources.tools import tokenizer

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.wenxin_langchain_instance import WenXinLangChainInstance

TokenModelList = [
    'ernie-4.5-turbo-32k'
    'ernie-4.5-8k-preview'
    'ernie-4.0-8k',
    'ernie-3.5-8k',
    'ernie-speed-8k',
    'ernie-speed-128k',
    'ernie-lite-8k',
    'ernie-tiny-8k',
    'ernie-char-8k',
]


class WenXinLLM(LLM):
    """WenXin LLM wrapper for LangChain.
        This is a wrapper around the Qianfan Chat Completion API.
        It uses the QianfanChatEndpoint class from the langchain_community package.
        It also supports streaming and token counting.
        It can be used with any other LangChain tools or agents.

        Attributes:
            api_key (str): The access key of the Qianfan API.
                Defaults to the value of the QIANFAN_AK environment variable.
            secret_key (str): The secret key of the Qianfan API.
                Defaults to the value of the QIANFAN_SK environment variable.
    """
    api_key: str = Field(default_factory=lambda: get_from_env("QIANFAN_AK"))
    secret_key: str = Field(default_factory=lambda: get_from_env("QIANFAN_SK"))

    def _new_client(self):
        if self.client is None:
            self.client = qianfan.ChatCompletion(ak=self.api_key, sk=self.secret_key)
        """Create a new Qianfan client."""
        return self.client

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.client = self._new_client()
        client = self.client
        chat_completion = client.do(
            messages=messages,
            model=kwargs.pop('model', self.model_name),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            **kwargs,
        )
        if not streaming:
            return self.parse_result(chat_completion)
        return self.generate_stream_result(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        self.async_client = self._new_client()
        async_client = self.async_client
        chat_completion = await async_client.ado(
            messages=messages,
            model=kwargs.pop('model', self.model_name),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            **kwargs,
        )
        if not streaming:
            return self.parse_result(chat_completion)
        return self.agenerate_stream_result(chat_completion)

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        res = self._new_client().get_model_info(self.model_name)
        if res.max_input_tokens:
            return res.max_input_tokens
        return res.max_input_chars

    def get_num_tokens(self, text: str) -> int:
        model_name = ''
        if self.model_name.lower() in TokenModelList:
            model_name = self.model_name.lower()
        token_cnt = tokenizer.Tokenizer().count_tokens(
            text=text,
            mode='remote',
            model=model_name
        )
        return token_cnt

    @staticmethod
    def parse_result(chunk: QfResponse):
        text = chunk.body.get('result')
        if not text:
            return None
        return LLMOutput(text=text, raw=chunk)

    def generate_stream_result(self, chat_completion) -> Iterator[LLMOutput]:
        for chunk in chat_completion:
            data = self.parse_result(chunk)
            if data:
                yield data

    async def agenerate_stream_result(self, chat_completion: AsyncIterator) -> AsyncIterator[LLMOutput]:
        async for chunk in chat_completion:
            data = self.parse_result(chunk)
            if data:
                yield data

    def as_langchain(self) -> BaseLanguageModel:
        """Return an instance of the LangChain `BaseLanguageModel` class."""
        self.init_channel()
        if self._channel_instance:
            return self._channel_instance.as_langchain()
        return WenXinLangChainInstance(llm=self)

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'WenXinLLM':
        super().initialize_by_component_configer(component_configer)
        if 'api_key' in component_configer.configer.value:
            api_key = component_configer.configer.value.get('api_key')
            self.api_key = process_yaml_func(api_key, component_configer.yaml_func_instance)
        if 'secret_key' in component_configer.configer.value:
            secret_key = component_configer.configer.value.get('secret_key')
            self.secret_key = process_yaml_func(secret_key, component_configer.yaml_func_instance)
        return self
