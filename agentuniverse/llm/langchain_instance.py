# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: langchain_instance.py

from typing import Any, List, Optional, AsyncIterator

from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.schema import BaseMessage, ChatResult
from langchain_community.chat_models.openai import _convert_delta_to_message_chunk
from langchain_core.language_models.chat_models import generate_from_stream, agenerate_from_stream
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk

from agentuniverse.llm.llm import LLM


class LangchainOpenAI(ChatOpenAI):
    """Langchain OpenAI LLM wrapper."""

    llm: Optional[LLM] = None

    def __init__(self, llm: LLM):
        """The __init__ method.

        The agentUniverse LLM instance is passed to this class as an argument.
        Convert the attributes of agentUniverse(aU) LLM instance to the LangchainOpenAI object for initialization

        Args:
            llm (LLM): the agentUniverse(aU) LLM instance.
        """
        init_params = dict()
        init_params["model_name"] = llm.model_name if llm.model_name else "gpt-3.5-turbo"
        init_params["temperature"] = llm.temperature if llm.temperature else 0.7
        init_params["request_timeout"] = llm.request_timeout
        init_params["max_tokens"] = llm.max_tokens
        init_params["max_retries"] = llm.max_retries if llm.max_retries else 2
        init_params["streaming"] = llm.streaming if llm.streaming else False
        init_params["openai_api_key"] = llm.openai_api_key if llm.openai_api_key else "blank"
        init_params["openai_organization"] = llm.openai_organization
        init_params["openai_api_base"] = llm.openai_api_base
        init_params["openai_proxy"] = llm.openai_proxy
        super().__init__(**init_params)
        self.llm = llm

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs,
    ) -> ChatResult:
        """Run the Langchain OpenAI LLM."""
        should_stream = stream if stream is not None else self.streaming
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        llm_output = self.llm.call(messages=message_dicts, **params)
        if not should_stream:
            return self._create_chat_result(llm_output.raw)
        stream_iter = self.as_langchain_chunk(llm_output)
        return generate_from_stream(stream_iter)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Asynchronously run the Langchain OpenAI LLM."""
        should_stream = stream if stream is not None else self.streaming
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        llm_output = await self.llm.acall(messages=message_dicts, **params)
        if not should_stream:
            return self._create_chat_result(llm_output.raw)
        stream_iter = self.as_langchain_achunk(llm_output)
        return await agenerate_from_stream(stream_iter)

    @staticmethod
    def as_langchain_chunk(stream, run_manager=None):
        default_chunk_class = AIMessageChunk
        for llm_result in stream:
            chunk = llm_result.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(choice["delta"], default_chunk_class)
            finish_reason = choice.get("finish_reason")
            generation_info = dict(finish_reason=finish_reason) if finish_reason is not None else None
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info)
            yield chunk
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)

    @staticmethod
    async def as_langchain_achunk(
        stream_iterator: AsyncIterator, run_manager=None
    ) -> AsyncIterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk
        async for llm_result in stream_iterator:
            chunk = llm_result.raw
            if not isinstance(chunk, dict):
                chunk = chunk.dict()
            if len(chunk["choices"]) == 0:
                continue
            choice = chunk["choices"][0]
            chunk = _convert_delta_to_message_chunk(choice["delta"], default_chunk_class)
            finish_reason = choice.get("finish_reason")
            generation_info = dict(finish_reason=finish_reason) if finish_reason is not None else None
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info)
            yield chunk
            if run_manager:
                await run_manager.on_llm_new_token(token=chunk.text, chunk=chunk)
