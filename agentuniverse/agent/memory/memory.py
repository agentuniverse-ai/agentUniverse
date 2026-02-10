# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 10:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory.py
from typing import Optional, List
from pydantic import Extra

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.memory.enum import MemoryTypeEnum
from agentuniverse.agent.memory.memory_compressor.memory_compressor import MemoryCompressor
from agentuniverse.agent.memory.memory_compressor.memory_compressor_manager import MemoryCompressorManager
from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import MemoryStorageManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.util.memory_util import get_memory_tokens, get_memory_string


class Memory(ComponentBase):
    """The base class for memory.

    Memory manages conversation history for an agent's session.

    Attributes:
        name: The name of the memory instance.
        description: The description of the memory.
        memory_key: The key name used when injecting memory into prompt context.
        max_tokens: The maximum token budget for memory content.
        agent_llm_name: The LLM name used for token counting.
        memory_compressor: The name of the memory compressor instance.
        memory_storages: The name list of the memory storage instances.
        memory_retrieval_storage: The name of the memory retrieval storage instance.
        summarize_agent_id: The agent used to generate memory summaries.
    """

    name: Optional[str] = ""
    description: Optional[str] = None
    type: MemoryTypeEnum = None
    memory_key: Optional[str] = 'chat_history'
    max_tokens: int = 2000
    agent_llm_name: Optional[str] = None
    memory_compressor: Optional[str] = None
    memory_storages: Optional[List[str]] = ['ram_memory_storage']
    memory_retrieval_storage: Optional[str] = None
    summarize_agent_id: Optional[str] = 'memory_summarize_agent'

    class Config:
        extra = Extra.allow

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.MEMORY, **kwargs)


    def add(self, message_list: List[Message], session_id: str = None, agent_id: str = None,
            **kwargs) -> None:
        """Add messages to the memory."""
        if not message_list:
            return
        for storage_name in self.memory_storages:
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(storage_name)
            if memory_storage:
                memory_storage.add(message_list, session_id, agent_id, **kwargs)

    def delete(self, session_id: str = None, **kwargs) -> None:
        """Delete messages from the memory."""
        for storage_name in self.memory_storages:
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(storage_name)
            if memory_storage:
                memory_storage.delete(session_id, **kwargs)

    def get(self, session_id: str = None, agent_id: str = None,
            prune: bool = False, token_budget: int = None, **kwargs) -> List[Message]:
        """Get messages from the memory.

        Args:
            session_id: The session identifier.
            agent_id: The agent identifier.
            prune: Whether to prune messages to fit token budget.
            token_budget: External token budget override. Falls back to self.max_tokens.

        Returns:
            List of messages, pruned if requested.
        """
        memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(
            self.memory_retrieval_storage
        )
        if not memory_storage:
            return []
        memories = memory_storage.get(session_id, agent_id, **kwargs)
        if prune:
            memories = self.prune(memories, token_budget=token_budget)
        return memories


    async def aadd(self, message_list: List[Message], session_id: str = None,
                   agent_id: str = None, **kwargs) -> None:
        """Async version of add()."""
        if not message_list:
            return
        for storage_name in self.memory_storages:
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(storage_name)
            if memory_storage:
                await memory_storage.aadd(message_list, session_id, agent_id, **kwargs)

    async def adelete(self, session_id: str = None, **kwargs) -> None:
        """Async version of delete()."""
        for storage_name in self.memory_storages:
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(storage_name)
            if memory_storage:
                await memory_storage.adelete(session_id, **kwargs)

    async def aget(self, session_id: str = None, agent_id: str = None,
                   prune: bool = False, token_budget: int = None, **kwargs) -> List[Message]:
        """Async version of get()."""
        memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(
            self.memory_retrieval_storage
        )
        if not memory_storage:
            return []
        memories = await memory_storage.aget(session_id, agent_id, **kwargs)
        if prune:
            memories = self.prune(memories, token_budget=token_budget)
        return memories

    # ============ Token 裁剪 ============

    def prune(self, memories: List[Message], token_budget: int = None) -> List[Message]:
        """Prune messages to fit within token budget.

        Strategy: remove oldest messages first, optionally compress them
        into a summary via memory_compressor.

        Args:
            memories: The full list of messages.
            token_budget: Max tokens allowed. Falls back to self.max_tokens.

        Returns:
            Pruned list of messages within budget.
        """
        if not memories:
            return []

        budget = token_budget or self.max_tokens
        new_memories = memories[:]
        tokens = get_memory_tokens(new_memories, self.agent_llm_name)

        if tokens <= budget:
            return new_memories

        pruned_messages = []
        while new_memories and tokens > budget:
            pruned_messages.append(new_memories.pop(0))
            tokens = get_memory_tokens(new_memories, self.agent_llm_name)

        if pruned_messages and self.memory_compressor:
            memory_compressor: MemoryCompressor = MemoryCompressorManager().get_instance_obj(
                self.memory_compressor
            )
            if memory_compressor:
                remaining_budget = budget - tokens
                compressed_content = memory_compressor.compress_memory(
                    pruned_messages, remaining_budget
                )
                if compressed_content:
                    new_memories.insert(0, Message.system(
                        content=f"[Summary of earlier conversation]\n{compressed_content}"
                    ))

        return new_memories

    # ============ 配置与拷贝 ============

    def set_by_agent_model(self, **kwargs) -> 'Memory':
        """Create a copy with agent-level overrides applied."""
        copied_obj = self.create_copy()
        for field in ('memory_key', 'max_tokens', 'agent_llm_name'):
            if field in kwargs and kwargs[field]:
                setattr(copied_obj, field, kwargs[field])
        return copied_obj

    def summarize_memory(self, session_id: str, agent_id: str = None,
                  **kwargs) -> str:
        """Generate a summary of the conversation memory.

        Uses a dedicated summarize agent to produce a condensed version
        of the full conversation history, incorporating any existing summary.

        Args:
            session_id: The session identifier.
            agent_id: The agent identifier.

        Returns:
            The summarized content string.
        """
        messages = self.get(session_id=session_id, agent_id=agent_id, **kwargs)
        summarize_messages = self.get(
            session_id=session_id, agent_id=agent_id, type='summarize'
        )
        summarize_content = (
            summarize_messages[-1].content if summarize_messages else ''
        )
        messages_str = get_memory_string(messages)
        agent: 'Agent' = AgentManager().get_instance_obj(
            self.summarize_agent_id)
        output_object: OutputObject = agent.run(
            input=messages_str, summarize_content=summarize_content
        )
        return output_object.get_data('output')

    async def async_summarize_memory(self, session_id: str, agent_id: str = None, **kwargs) -> str:
        """Async version of summarize()."""
        messages = await self.aget(session_id=session_id, agent_id=agent_id, **kwargs)
        summarize_messages = await self.aget(
            session_id=session_id, agent_id=agent_id, type='summarize'
        )
        summarize_content = (
            summarize_messages[-1].content if summarize_messages else ''
        )
        messages_str = get_memory_string(messages)
        agent: 'Agent' = AgentManager().get_instance_obj(self.summarize_agent_id)
        output_object: OutputObject = await agent.async_run(
            input=messages_str, summarize_content=summarize_content
        )
        return output_object.get_data('output')

    def get_instance_code(self) -> str:
        """Return the full name of the memory."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: MemoryConfiger) -> 'Memory':
        """Initialize the memory by the ComponentConfiger object.
        Args:
            component_configer: the MemoryConfiger object

        Returns:
            Memory: the initialized Memory object
        """
        field_mapping = {
            'name': 'name',
            'description': 'description',
            'memory_key': 'memory_key',
            'max_tokens': 'max_tokens',
            'memory_compressor': 'memory_compressor',
            'memory_storages': 'memory_storages',
            'memory_retrieval_storage': 'memory_retrieval_storage',
        }
        for configer_field, self_field in field_mapping.items():
            value = getattr(component_configer, configer_field, None)
            if value:
                setattr(self, self_field, value)
        if component_configer.type:
            self.type = next((member for member in MemoryTypeEnum if member.value == component_configer.type))
        if not self.memory_retrieval_storage and self.memory_storages:
            self.memory_retrieval_storage = self.memory_storages[0]
        if component_configer.memory_summarize_agent:
            self.summarize_agent_id = component_configer.memory_summarize_agent
        return self

    def create_copy(self):
        copied = self.model_copy()
        if self.memory_storages is not None:
            copied.memory_storages = self.memory_storages.copy()
        return copied
