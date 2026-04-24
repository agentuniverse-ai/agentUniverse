# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 10:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory.py
from typing import Optional, List
from langchain_core.memory import BaseMemory
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
    """The basic class for memory model.

    Attributes:
        name (Optional[str]): The name of the memory class.
        description (Optional[str]): The description of the memory class.
        type (MemoryTypeEnum): The type of the memory class including `long-term` and `short-term`.
        memory_key (Optional[str]): The name of the memory key in the prompt.
        max_tokens (int): The maximum number of tokens allowed in the prompt.
        memory_compressor (Optional[str]): The name of the memory compressor instance.
        memory_storages (Optional[str]): The name list of the memory storage instances.
        memory_retrieval_storage (Optional[str]): The name of the memory retrieval storage instance.
    """

    name: Optional[str] = ""
    description: Optional[str] = None
    type: MemoryTypeEnum = None
    memory_key: Optional[str] = 'chat_history'
    max_tokens: int = 2000
    memory_compressor: Optional[str] = None
    memory_storages: Optional[List[str]] = ['ram_memory_storage']
    memory_retrieval_storage: Optional[str] = None
    summarize_agent_id: Optional[str] = 'memory_summarize_agent'
    context_manager_name: Optional[str] = None  # NEW: Link to ContextManager (Phase 2)

    class Config:
        extra = Extra.allow

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.MEMORY, **kwargs)

    def as_langchain(self) -> BaseMemory:
        """Convert the agentUniverse(aU) memory class to the langchain memory class."""
        pass

    def add(self, message_list: List[Message], session_id: str = None, agent_id: str = None,
            **kwargs) -> None:
        """Add messages to the memory."""
        if not message_list:
            return
        for storage in self.memory_storages:
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(storage)
            if memory_storage:
                memory_storage.add(message_list, session_id, agent_id, **kwargs)

    def delete(self, session_id: str = None, **kwargs) -> None:
        """Delete messages from the memory."""
        for storage in self.memory_storages:
            memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(storage)
            if memory_storage:
                memory_storage.delete(session_id, **kwargs)

    def get(self, session_id: str = None, agent_id: str = None, prune: bool = False, **kwargs) -> List[Message]:
        """Get messages from the memory."""
        memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(self.memory_retrieval_storage)
        if memory_storage:
            memories = memory_storage.get(session_id, agent_id, **kwargs)
            if prune:
                memories = self.prune(memories)
            return memories
        return []

    def get_with_no_prune(self, session_id: str = None, agent_id: str = None, **kwargs) -> List[Message]:
        """Get messages from the memory."""
        memory_storage: MemoryStorage = MemoryStorageManager().get_instance_obj(self.memory_retrieval_storage)
        if memory_storage:
            memories = memory_storage.get(session_id, agent_id, **kwargs)
            return memories
        return []

    def prune(self, memories: List[Message]) -> List[Message]:
        if not memories:
            return []
        new_memories = memories[:]

        agent_llm_name = self.agent_llm_name if hasattr(self, 'agent_llm_name') else None
        tokens = get_memory_tokens(new_memories, agent_llm_name)

        if tokens <= self.max_tokens:
            return new_memories

        pruned_memories = []
        while tokens > self.max_tokens:
            pruned_memory = new_memories.pop(0)
            pruned_memories.append(pruned_memory)
            tokens = get_memory_tokens(new_memories, agent_llm_name)

        if pruned_memories:
            memory_compressor: MemoryCompressor = MemoryCompressorManager().get_instance_obj(self.memory_compressor)
            if memory_compressor:
                compressed_memory = memory_compressor.compress_memory(pruned_memories, self.max_tokens - tokens)
                if compressed_memory:
                    new_memories.insert(0, Message(content=compressed_memory))
        return new_memories

    def get_with_context_budget(
        self,
        session_id: str,
        agent_id: str,
        allocated_tokens: int,
        **kwargs
    ) -> List[Message]:
        """Retrieve memory within allocated token budget (Phase 2 integration).

        This method integrates with ContextManager's budget allocation system,
        replacing reactive max_tokens pruning with proactive budget management.

        Args:
            session_id: Session identifier
            agent_id: Agent identifier
            allocated_tokens: Token budget allocated by ContextManager
            **kwargs: Additional retrieval parameters

        Returns:
            List[Message]: Messages within allocated budget (most recent first)

        Example:
            >>> # In Agent.run() with ContextManager
            >>> window = context_manager.get_context_window(session_id)
            >>> memory_budget = window.component_budgets.get('memory', 2000)
            >>> messages = memory.get_with_context_budget(
            ...     session_id, agent_id, memory_budget
            ... )
        """
        # If linked to context manager, use budget-aware retrieval
        if self.context_manager_name:
            try:
                from agentuniverse.agent.context.context_manager_manager import ContextManagerManager
                from agentuniverse.agent.context.context_model import ContextType, ContextPriority

                ctx_mgr = ContextManagerManager().get_instance_obj(self.context_manager_name)
                if ctx_mgr:
                    # Retrieve conversation context from ContextManager
                    segments = ctx_mgr.get_context(
                        session_id,
                        context_type=ContextType.CONVERSATION,
                        limit=1000,  # Get all conversation segments
                        **kwargs
                    )

                    # Convert segments to Messages
                    messages = []
                    for seg in segments:
                        # Parse role from metadata if available
                        role = seg.metadata.extra_data.get('role', 'assistant') if hasattr(seg.metadata, 'extra_data') else 'assistant'
                        messages.append(Message(
                            content=seg.content,
                            type=role
                        ))

                    # Select messages within budget (most recent first)
                    selected_messages = []
                    current_tokens = 0
                    agent_llm_name = self.agent_llm_name if hasattr(self, 'agent_llm_name') else None

                    for message in messages:
                        message_tokens = get_memory_tokens([message], agent_llm_name)
                        if current_tokens + message_tokens <= allocated_tokens:
                            selected_messages.append(message)
                            current_tokens += message_tokens
                        else:
                            break  # Budget exceeded

                    return selected_messages

            except Exception:
                pass  # Fall back to traditional retrieval

        # Fallback: Original pruning logic (backward compatible)
        memories = self.get(session_id, agent_id, prune=False, **kwargs)

        # Prune to allocated tokens
        if not memories:
            return []

        selected_memories = []
        current_tokens = 0
        agent_llm_name = self.agent_llm_name if hasattr(self, 'agent_llm_name') else None

        # Select most recent messages within budget
        for memory in reversed(memories):
            memory_tokens = get_memory_tokens([memory], agent_llm_name)
            if current_tokens + memory_tokens <= allocated_tokens:
                selected_memories.insert(0, memory)
                current_tokens += memory_tokens
            else:
                break

        return selected_memories

    def set_by_agent_model(self, **kwargs):
        """ Assign values of parameters to the Memory model in the agent configuration."""
        # note: default shallow copy
        copied_obj = self.model_copy()
        if 'memory_key' in kwargs and kwargs['memory_key']:
            copied_obj.memory_key = kwargs['memory_key']
        if 'max_tokens' in kwargs and kwargs['max_tokens']:
            copied_obj.max_tokens = kwargs['max_tokens']
        if 'agent_llm_name' in kwargs and kwargs['agent_llm_name']:
            copied_obj.agent_llm_name = kwargs['agent_llm_name']
        return copied_obj

    def summarize_memory(self, **kwargs) -> str:
        kwargs['prune'] = False
        messages = self.get(**kwargs)
        summarize_messages = self.get(session_id=kwargs.get('session_id'), agent_id=kwargs.get('agent_id'),
                                      type='summarize')
        summarize_content = summarize_messages[-1].content if summarize_messages and len(summarize_messages) > 0 else ''
        messages_str = get_memory_string(messages)
        agent: 'Agent' = AgentManager().get_instance_obj(self.summarize_agent_id)
        output_object: OutputObject = agent.run(input=messages_str, summarize_content=summarize_content)
        return output_object.get_data('output')

    def get_instance_code(self) -> str:
        """Return the full name of the memory."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: MemoryConfiger) -> 'Memory':
        """Initialize the memory by the ComponentConfiger object.
        Args:
            component_configer(MemoryConfiger): the ComponentConfiger object
        Returns:
            Memory: the Memory object
        """
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if component_configer.type:
            self.type = next((member for member in MemoryTypeEnum if member.value == component_configer.type))
        if component_configer.memory_key:
            self.memory_key = component_configer.memory_key
        if component_configer.max_tokens:
            self.max_tokens = component_configer.max_tokens
        if component_configer.memory_compressor:
            self.memory_compressor = component_configer.memory_compressor
        if component_configer.memory_storages:
            self.memory_storages = component_configer.memory_storages
        if component_configer.memory_retrieval_storage:
            self.memory_retrieval_storage = component_configer.memory_retrieval_storage
        if not self.memory_retrieval_storage:
            self.memory_retrieval_storage = self.memory_storages[0]
        if component_configer.memory_summarize_agent:
            self.summarize_agent_id = component_configer.memory_summarize_agent
        # NEW: Phase 2 integration
        if hasattr(component_configer, 'context_manager') and component_configer.context_manager:
            self.context_manager_name = component_configer.context_manager
        return self

    def create_copy(self):
        copied = self.model_copy()
        if self.memory_storages is not None:
            copied.memory_storages = self.memory_storages.copy()
        return copied
