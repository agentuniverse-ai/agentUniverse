# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/7 19:28
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: ollama_channel_langchain_instance.py
from typing import List, Optional, Iterator, Any, AsyncIterator

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel


class OllamaChannelLangchainInstance(ChatOllama):
    """A ChatOllama based langchain instance routing calls through an LLMChannel."""

    llm_channel: LLMChannel = None

    def __init__(self, llm_channel: LLMChannel):
        """Initialize the instance with the underlying LLM channel.

        Args:
            llm_channel: the LLM channel this instance calls through.
        """
        super().__init__()
        self.llm_channel = llm_channel
        self.model = llm_channel.channel_model_name

    def _create_chat_stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> Iterator[str]:
        """Create a synchronous stream of raw responses from the LLM channel.

        Args:
            messages: the chat messages to send to the channel.
            stop: optional stop sequences forwarded to the channel.
            **kwargs: extra arguments forwarded to the channel call.

        Returns:
            An iterator yielding the raw response of each channel output.
        """
        data = self.llm_channel.call(
            messages=self._convert_messages_to_ollama_messages(messages), stop=stop, **kwargs
        )
        for llm_output in data:
            yield llm_output.raw

    async def _acreate_chat_stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Create an asynchronous stream of raw responses from the LLM channel.

        Args:
            messages: the chat messages to send to the channel.
            stop: optional stop sequences forwarded to the channel.
            **kwargs: extra arguments forwarded to the channel call.

        Returns:
            An async iterator yielding the raw response of each channel output.
        """
        data = await self.llm_channel.acall(
            messages=self._convert_messages_to_ollama_messages(messages), stop=stop, **kwargs
        )
        async for llm_output in data:
            yield llm_output.raw
