# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 11:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: langchain_instance.py
from typing import List, Optional, Dict, Any

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain.memory import ConversationSummaryBufferMemory, ConversationTokenBufferMemory
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


class AuConversationSummaryBufferMemory(ConversationSummaryBufferMemory):
    """Long term memory to store conversation memory.

    If memories exceeds the max tokens limit,
    memories will be compressed by the AuConversationSummaryBufferMemory.predict_new_summary method.

    Attributes:
        messages (List[BaseMessage]): List of BaseMessage to save.
    """

    messages: Optional[List[Message]] = None
    prompt_version: Optional[str] = None

    def __init__(self, **kwargs):
        """The __init__ method.

        The initialization method saves the memory context from messages in `messages` attribute to the memory buffer.

        Args:
            **kwargs: Arbitrary keyword arguments.
        """

        super().__init__(**kwargs)
        self.build_memory()

    @property
    def load_memory(self) -> List[BaseMessage]:
        """General method: load the memory context from the memory buffer."""
        messages = self.chat_memory.messages
        if self.moving_summary_buffer != "":
            moving_messages: List[BaseMessage] = [self.summary_message_cls(content=self.moving_summary_buffer)]
            messages = moving_messages + messages
        return messages

    @property
    def load_memory_str(self) -> str:
        """General method: load the memory context from the memory buffer as string format."""
        buffer = get_buffer_string(self.chat_memory.messages)
        if self.moving_summary_buffer is not None:
            buffer = self.moving_summary_buffer + buffer
        return buffer

    def build_memory(self):
        """Save the memory context from messages in `messages` attribute to the memory buffer.

        Note:
            If conversation messages contains the system message, it will be saved in the `moving_summary_buffer` attribute.
        """
        if self.messages is None:
            return
        # save system messages
        for message in self.messages:
            if message.type.lower() == ChatMessageEnum.SYSTEM.value:
                self.moving_summary_buffer += message.content
                self.messages.remove(message)
        # generate pairs of Human and AI conversation messages and save to the memory buffer
        for i in range(0, len(self.messages), 2):
            inputs, outputs = self.generate_chat_messages(self.messages[i], self.messages[i + 1])
            self.save_context(inputs, outputs)

    def generate_chat_messages(self, *pairs: Message):
        """generate pairs of Human and AI conversation messages"""
        human_dict = {}
        ai_dict = {}
        for pair in pairs:
            if pair.type.lower() == ChatMessageEnum.HUMAN.value:
                human_dict = {self.input_key: pair.content}
            elif pair.type.lower() == ChatMessageEnum.AI.value:
                ai_dict = {self.output_key: pair.content}

        return human_dict, ai_dict

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from the conversation to buffer and prune memories"""

        def message_to_dict(message):
            return {"content": message.content, "type": message.type}

        super().save_context(inputs, outputs)
        message_list = self.load_memory
        messages_dicts = [message_to_dict(message) for message in message_list]
        inputs[self.memory_key] = messages_dicts

    def predict_new_summary(self, messages: List[BaseMessage], existing_summary: str) -> str:
        """Predict new summary, summarize memories in multiple rounds of conversations."""
        new_lines = get_buffer_string(
            messages,
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )
        prompt_version = self.prompt_version if self.prompt_version else "chat_memory.summarizer_cn"
        prompt: Prompt = PromptManager().get_instance_obj(prompt_version)
        chain = prompt.as_langchain() | self.llm | StrOutputParser()
        return chain.invoke(input={"summary": existing_summary, "new_lines": new_lines, "max_tokens": 500})


class AuConversationTokenBufferMemory(ConversationTokenBufferMemory):
    """Short term memory to store conversation memory.

    If memories exceeds the max tokens limit, the requirement is met by truncating part of memories

    Attributes:
        messages (List[BaseMessage]): List of BaseMessage to save.
    """

    messages: Optional[List[Message]] = None

    def __init__(self, **kwargs):
        """The __init__ method.

        The initialization method saves the memory context from messages in `messages` attribute to the memory buffer.

        Args:
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(**kwargs)
        self.build_memory()

    @property
    def load_memory(self) -> List[BaseMessage]:
        """General method: load the memory context from the memory buffer."""
        return self.chat_memory.messages

    @property
    def load_memory_str(self) -> str:
        """General method: load the memory context from the memory buffer as string format."""
        return get_buffer_string(self.chat_memory.messages)

    def build_memory(self):
        """Save the memory context from messages in `messages` attribute to the memory buffer.

        Note:
            If conversation messages contains the system message, it will be discarded from the memory.
        """
        if self.messages is None:
            return
        # discard system messages
        for message in self.messages:
            if message.type.lower() == ChatMessageEnum.SYSTEM.value:
                self.messages.remove(message)
        # generate pairs of Human and AI conversation messages and save to the memory buffer
        for i in range(0, len(self.messages), 2):
            inputs, outputs = self.generate_chat_messages(self.messages[i], self.messages[i + 1])
            self.save_context(inputs, outputs)

    def generate_chat_messages(self, *pairs: Message):
        """generate pairs of Human and AI conversation messages"""
        human_dict = {}
        ai_dict = {}
        for pair in pairs:
            if pair.type == ChatMessageEnum.HUMAN.value:
                human_dict = {self.input_key: pair.content}
            elif pair.type == ChatMessageEnum.AI.value:
                ai_dict = {self.output_key: pair.content}

        return human_dict, ai_dict

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from the conversation to buffer and truncate part of memories."""

        def message_to_dict(message):
            return {"content": message.content, "type": message.type}

        super().save_context(inputs, outputs)
        message_list = self.load_memory
        messages_dicts = [message_to_dict(message) for message in message_list]
        inputs[self.memory_key] = messages_dicts
