# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/7 19:26
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: ollama_llm_channel.py
import json
from typing import Optional, Union, Iterator, AsyncIterator

from langchain_core.language_models import BaseLanguageModel
from ollama import Options

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.llm.llm_channel.langchain_instance.ollama_channel_langchain_instance import \
    OllamaChannelLangchainInstance
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_output import LLMOutput


class OllamaLLMChannel(LLMChannel):
    channel_api_base: Optional[str] = "http://localhost:11434"

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'OllamaLLMChannel':
        super()._initialize_by_component_configer(component_configer)
        return self

    def as_langchain(self) -> BaseLanguageModel:
        return OllamaChannelLangchainInstance(self)

    def _new_client(self):
        if self.client:
            return self.client
        from ollama import Client
        return Client(
            host=self.channel_api_base,
        )

    def _new_async_client(self):
        if self.async_client:
            return self.async_client
        from ollama import AsyncClient
        return AsyncClient(
            host=self.channel_api_base,
        )

    def _options(self):
        return Options(**{
            "num_ctx": self.max_context_length(),
            "num_predict": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.request_timeout,
            **(self.ext_info if self.ext_info else {}),
        })

    def _call(self, messages, stop=None, **kwargs) -> Union[LLMOutput, Iterator[LLMOutput]]:
        should_stream = kwargs.pop("stream", self.streaming)
        client = self._new_client()
        options = self._options()
        options.setdefault("stop", stop)
        res = client.chat(model=self.channel_model_name, messages=messages, options=options, stream=should_stream)
        if should_stream:
            return self.generate_result(res)
        else:
            return LLMOutput(text=res.get("message").get('content'), raw=json.dumps(res),
                             message=Message.from_dict(res.get("message")))

    async def _acall(self, messages, stop=None, **kwargs) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        client = self._new_async_client()
        should_stream = kwargs.pop("stream", self.streaming)
        options = self._options()
        options.setdefault("stop", stop)
        res = await client.chat(model=self.channel_model_name, messages=messages, options=options, stream=should_stream)
        if not should_stream:
            return LLMOutput(text=res.get("message").get('content'), raw=json.dumps(res),
                             message=Message.from_dict(res.get("message")))
        if should_stream:
            return self.agenerate_result(res)

    def generate_result(self, data):
        for line in data:
            yield LLMOutput(text=line.get("message").get('content'), raw=json.dumps(line),
                            message=Message.from_dict(line.get("message")))

    async def agenerate_result(self, data):
        async for line in data:
            yield LLMOutput(text=line.get("message").get('content'), raw=json.dumps(line),
                            message=Message.from_dict(line.get("message")))
