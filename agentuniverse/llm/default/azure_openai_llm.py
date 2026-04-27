# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from typing import Any, Union, Iterator, AsyncIterator, Optional, AsyncGenerator

from langchain_core.messages import AIMessageChunk
from pydantic import Field

from langchain_openai import AzureChatOpenAI
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput


# @Time    : 2025/11/6 14:57
# @Author  : xieshenghao
# @Email   : xieshenghao.xsh@antgroup.com
# @FileName: azure_openai_llm.py

AZURE_OPENAI_MAX_CONTEXT_LENGTH = {
    "gpt-5": 272000,
    "gpt-5-mini": 272000,
    "gpt-5-nano": 272000,
    "gpt-5-pro": 272000,
    "gpt-4.1": 1047576,
    "gpt-4.1-nano": 1047576,
    "gpt-4.1-mini": 1047576,
}

class AzureOpenAILLM(LLM):
    """
    Azure OpenAI LLM
    Args:
        azure_openai_endpoint(Optional[str]): API ENDPOINT for the model. Defaults to None.
        azure_openai_api_key(Optional[str]): API KEY for the model. Defaults to None.
        azure_api_version(Optional[str]): API VERSION for the model. Defaults to None.
        azure_openai_base_url(Optional[str]): API BASE URL for the model. Defaults to None.

    """
    azure_openai_endpoint: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_OPENAI_ENDPOINT"))
    azure_openai_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_OPENAI_API_KEY"))
    azure_api_version: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_API_VERSION"))
    azure_openai_base_url: Optional[str] = Field(default_factory=lambda: get_from_env("AZURE_OPENAI_BASE_URL"))
    ext_params: Optional[dict] = {}
    ext_headers: Optional[dict] = {}
    client: AzureChatOpenAI = None


    def __init__(self, **data):
        super().__init__(**data)

    def _get_client(self):
        """
        create an AzureChatOpenAI client if not exists.
        """
        if self.client is None:
            self._client = AzureChatOpenAI(
                azure_endpoint=self.azure_openai_endpoint,
                api_key=self.azure_openai_api_key,
                azure_deployment=self.model_name,
                api_version=self.azure_api_version,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 512,
                timeout=self.request_timeout,
                max_retries=self.max_retries,
            )
        return self._client

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """ The call method of Azure OpenAI LLM.

        Users can customize how the model interacts by overriding call method of the LLM class.

        Args:
            messages (list): The messages send to the LLM.
            **kwargs: Arbitrary keyword arguments.

        """
        streaming = self._handle_stream(**kwargs)

        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop('extra_body', {})
        ext_params = {**ext_params, **extra_body}

        self.client = self._get_client()
        client = self.client

        if not streaming:
            response = client.invoke(messages, **ext_params)
            text = response.content
            return LLMOutput(text=text, raw=response)

        stream_raw_result = client.stream(input=messages)
        return self._generate_stream_result(stream_raw_result)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        streaming = self._handle_stream(**kwargs)

        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop('extra_body', {})
        ext_params = {**ext_params, **extra_body}

        self.client = self._get_client()
        client = self.client

        if not streaming:
            response = await client.ainvoke(messages, **ext_params)
            text =  response.content
            return LLMOutput(text=text, raw=response)
        stream_raw_result = client.astream(messages)
        return self.agenerate_stream_result(stream_raw_result)

    async def agenerate_stream_result(self, stream: AsyncIterator) -> AsyncIterator[LLMOutput]:
        """Generate the result of the stream."""
        async for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output

    def _generate_stream_result(self, stream) -> Iterator[LLMOutput]:
        for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output

    def max_context_length(self) -> int:
        if self._max_context_length:
            return self._max_context_length
        return AZURE_OPENAI_MAX_CONTEXT_LENGTH.get(self.model_name)

    def get_num_tokens(self, text: str) -> int:
        return AzureChatOpenAI.get_num_tokens(text=text)

    @staticmethod
    def parse_result(chunk: AIMessageChunk):
        """
            Generate the result of the stream.
        """
        text = chunk.content
        if text is None:
            text = ""
        return LLMOutput(text=text, raw=chunk)

    def _handle_stream(self, **kwargs: Any) -> bool:
        streaming = False
        if 'streaming_usage' in kwargs and kwargs.get('streaming_usage') is True:
            streaming = True
        if streaming and 'stream_options' not in self.ext_params:
            self.ext_params['stream_options'] = {
                "include_usage": True
            }
        return streaming