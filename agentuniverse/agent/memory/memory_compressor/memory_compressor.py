# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/9 19:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_compressor.py
from typing import Optional, List

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.memory_util import get_memory_string
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager


class MemoryCompressor(ComponentBase):
    """The basic class for the memory compressor.

    Attributes:
        name (str): The name of the memory compressor.
        description (str): The description of the memory compressor.
        compressor_prompt_version (str): The version of the prompt used for compressing the memory.
        compressor_llm_name (str): The name of the LLM used for compressing the memory.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    compressor_prompt_version: Optional[str] = None
    compressor_llm_name: Optional[str] = None
    component_type: ComponentEnum = ComponentEnum.MEMORY_COMPRESSOR

    SYSTEM_INSTRUCTION: str = '你是一个记忆压缩助手，请根据用户提供的对话记录和先前概要，生成精简的新记忆概要。'

    def _build_compress_messages(self, new_memories: List[Message], max_tokens: int = 500,
                                existing_memory: str = '') -> tuple:
        """Build prompt and messages for compression.

        Args:
            new_memories (List[Message]): The new memories to compress.
            max_tokens (int): The maximum number of tokens allowed in the compressed memory.
            existing_memory (str): The existing memory to append to.

        Returns:
            tuple: (llm, messages) or (None, None) if prompt/llm not available.
        """
        prompt: Prompt = PromptManager().get_instance_obj(self.compressor_prompt_version)
        llm: LLM = LLMManager().get_instance_obj(self.compressor_llm_name)
        if not (prompt and llm):
            return None, None

        new_memory_str = get_memory_string(new_memories)

        prompt_text = prompt.prompt_template.format(
            new_lines=new_memory_str,
            summary=existing_memory,
            max_tokens=max_tokens,
        )

        messages = [
            Message(type=ChatMessageEnum.SYSTEM, content=self.SYSTEM_INSTRUCTION),
            Message(type=ChatMessageEnum.USER, content=prompt_text),
        ]
        return llm, messages

    @staticmethod
    def _extract_compressed_text(output) -> str:
        """Extract compressed text from LLM output.

        Args:
            output: The LLMOutput from a call/acall.

        Returns:
            str: The compressed memory text.
        """
        if output and output.message and output.message.content:
            content = output.message.content_text
            return content if isinstance(content, str) else str(content)
        return ''

    def compress_memory(self, new_memories: List[Message], max_tokens: int = 500, existing_memory: str = '',
                        **kwargs) -> str:
        """Compress the memory.

        Args:
            new_memories (List[Message]): The new memories to compress.
            max_tokens (int): The maximum number of tokens allowed in the compressed memory.
            existing_memory (str): The existing memory to append to.

        Returns:
            str: The compressed memory.
        """
        llm, messages = self._build_compress_messages(new_memories, max_tokens, existing_memory)
        if llm is None:
            return ''

        output = llm.call(messages=messages, **kwargs)
        return self._extract_compressed_text(output)

    async def async_compress_memory(self, new_memories: List[Message], max_tokens: int = 500,
                                    existing_memory: str = '', **kwargs) -> str:
        """Asynchronously compress the memory using LLM.acall.

        Args:
            new_memories (List[Message]): The new memories to compress.
            max_tokens (int): The maximum number of tokens allowed in the compressed memory.
            existing_memory (str): The existing memory to append to.

        Returns:
            str: The compressed memory.
        """
        llm, messages = self._build_compress_messages(new_memories, max_tokens, existing_memory)
        if llm is None:
            return ''

        output = await llm.acall(messages=messages, **kwargs)
        return self._extract_compressed_text(output)

    def _initialize_by_component_configer(self, memory_compressor_config: ComponentConfiger) -> 'MemoryCompressor':
        """Initialize the MemoryCompressor by the ComponentConfiger object.

        Args:
            memory_compressor_config(ComponentConfiger): A configer contains memory_compressor basic info.
        Returns:
            MemoryCompressor: A MemoryCompressor instance.
        """
        if getattr(memory_compressor_config, 'name', None):
            self.name = memory_compressor_config.name
        if getattr(memory_compressor_config, 'description', None):
            self.description = memory_compressor_config.description
        if getattr(memory_compressor_config, 'compressor_prompt_version', None):
            self.compressor_prompt_version = memory_compressor_config.compressor_prompt_version
        if getattr(memory_compressor_config, 'compressor_llm_name', None):
            self.compressor_llm_name = memory_compressor_config.compressor_llm_name
        return self
