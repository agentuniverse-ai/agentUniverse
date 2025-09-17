# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/9 19:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_compressor.py
from typing import Optional, List

from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.memory_util import get_memory_string, get_memory_tokens
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

    def compress_memory(
        self, new_memories: List[Message], max_tokens: int = 500, existing_memory: str = "", **kwargs
    ) -> str:
        """Compress the memory.

        Args:
            new_memories (List[Message]): The new memories to compress.
            max_tokens (int): The maximum number of tokens allowed in the compressed memory.
            existing_memory (str): The existing memory to append to.

        Returns:
            str: The compressed memory.
        """
        prompt: Prompt = PromptManager().get_instance_obj(self.compressor_prompt_version)
        llm: LLM = LLMManager().get_instance_obj(self.compressor_llm_name)
        if prompt and llm:
            new_memory_str = get_memory_string(new_memories)
            chain = prompt.as_langchain() | llm.as_langchain() | StrOutputParser()
            result = chain.invoke(
                input={"new_lines": new_memory_str, "summary": existing_memory, "max_tokens": max_tokens}
            )
            return result
        else:
            return ""

    def _initialize_by_component_configer(self, memory_compressor_config: ComponentConfiger) -> "MemoryCompressor":
        """Initialize the MemoryCompressor by the ComponentConfiger object.

        Args:
            memory_compressor_config(ComponentConfiger): A configer contains memory_compressor basic info.
        Returns:
            MemoryCompressor: A MemoryCompressor instance.
        """
        if getattr(memory_compressor_config, "name", None):
            self.name = memory_compressor_config.name
        if getattr(memory_compressor_config, "description", None):
            self.description = memory_compressor_config.description
        if getattr(memory_compressor_config, "compressor_prompt_version", None):
            self.compressor_prompt_version = memory_compressor_config.compressor_prompt_version
        if getattr(memory_compressor_config, "compressor_llm_name", None):
            self.compressor_llm_name = memory_compressor_config.compressor_llm_name
        return self
