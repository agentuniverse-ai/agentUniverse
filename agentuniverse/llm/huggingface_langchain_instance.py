# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/05
# @FileName: huggingface_langchain_instance.py

"""Langchain chat model wrapper around the native HuggingFace aU llm component."""

from typing import Any, AsyncIterator, Iterator, List, Optional

from langchain_core.callbacks import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult

from agentuniverse.llm.llm import LLM


def _convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a langchain message into the huggingface chat message format."""
    role_mapping = {'human': 'user', 'ai': 'assistant', 'system': 'system', 'tool': 'tool'}
    role = role_mapping.get(message.type, message.type)
    return {'role': role, 'content': message.content}


class HuggingFaceLangchainInstance(BaseChatModel):
    """A langchain chat model delegating to the aU HuggingFace llm component."""

    llm: Optional[LLM] = None

    def __init__(self, llm: LLM, **kwargs: Any):
        super().__init__(**kwargs)
        self.llm = llm

    @property
    def _llm_type(self) -> str:
        return 'huggingface_hub'

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None,
                  run_manager: Optional[CallbackManagerForLLMRun] = None,
                  **kwargs: Any) -> ChatResult:
        output = self.llm.call(messages=[_convert_message_to_dict(m) for m in messages],
                               stop=stop, streaming=False, **kwargs)
        message = AIMessage(content=output.text or '')
        return ChatResult(generations=[ChatGeneration(message=message)])

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None,
                         run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
                         **kwargs: Any) -> ChatResult:
        output = await self.llm.acall(messages=[_convert_message_to_dict(m) for m in messages],
                                      stop=stop, streaming=False, **kwargs)
        message = AIMessage(content=output.text or '')
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _stream(self, messages: List[BaseMessage], stop: Optional[List[str]] = None,
                run_manager: Optional[CallbackManagerForLLMRun] = None,
                **kwargs: Any) -> Iterator[ChatGenerationChunk]:
        for output in self.llm.call(messages=[_convert_message_to_dict(m) for m in messages],
                                    stop=stop, streaming=True, **kwargs):
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=output.text or ''))
            if run_manager:
                run_manager.on_llm_new_token(output.text or '', chunk=chunk)
            yield chunk

    async def _astream(self, messages: List[BaseMessage], stop: Optional[List[str]] = None,
                       run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
                       **kwargs: Any) -> AsyncIterator[ChatGenerationChunk]:
        stream = await self.llm.acall(messages=[_convert_message_to_dict(m) for m in messages],
                                      stop=stop, streaming=True, **kwargs)
        async for output in stream:
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=output.text or ''))
            if run_manager:
                await run_manager.on_llm_new_token(output.text or '', chunk=chunk)
            yield chunk
