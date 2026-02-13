# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/15 10:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory.py
import warnings
from typing import Optional, List

from pydantic import ConfigDict

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.enum import MemoryTypeEnum
from agentuniverse.agent.memory.memory_compressor.memory_compressor import \
    MemoryCompressor
from agentuniverse.agent.memory.memory_compressor.memory_compressor_manager import \
    MemoryCompressorManager
from agentuniverse.agent.memory.memory_storage.legacy_hybrid_memory_storage import \
    LegacyHybridMemoryStorage
from agentuniverse.agent.memory.memory_storage.memory_storage import \
    MemoryStorage
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import \
    MemoryStorageManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.memory_configer import \
    MemoryConfiger
from agentuniverse.base.util.memory_util import get_memory_tokens, \
    get_memory_string


class Memory(ComponentBase):
    """The base class for memory.

    Memory gives an agent the sense of "the past". It manages the full
    lifecycle of conversation history: storing, retrieving, pruning, and
    building context that can be injected into prompts.

    Storage resolution (in priority order):
        1. ``memory_storage`` (new, recommended) — a single MemoryStorage name.
           All CRUD operations go through this one storage. It can be a simple
           storage or a user-defined composite (e.g. a custom HybridStorage
           with vector + KV backends).
        2. ``memory_storages`` + ``memory_retrieval_storage`` (legacy) — if
           ``memory_storage`` is not set, these legacy fields are used.  A
           ``LegacyHybridMemoryStorage`` is auto-constructed to wrap them,
           preserving the old fan-out-write / single-read behavior behind a
           unified MemoryStorage interface.

    Subclasses can override:
        - ``prune()`` for custom pruning strategies.
        - ``build_context()`` / ``async_build_context()`` for richer context
          structures.

    Attributes:
        name: The name of the memory instance.
        description: A human-readable description.
        type: The memory type enum value.
        memory_key: The key used when injecting memory into prompt context.
        max_tokens: The maximum token budget for memory content.
        agent_llm_name: The LLM name used for token counting.
        memory_compressor: The name of the memory compressor instance.
        memory_storage: The name of the single MemoryStorage to use (recommended).
        memory_storages: (Deprecated) List of storage names for write fan-out.
        memory_retrieval_storage: (Deprecated) Storage name for reads.
    """

    name: Optional[str] = ""
    description: Optional[str] = None
    type: Optional[MemoryTypeEnum] = None
    memory_key: Optional[str] = 'chat_history'
    max_tokens: int = 2000
    agent_llm_name: Optional[str] = None
    memory_compressor: Optional[str] = None

    # New: single storage entry point (recommended)
    memory_storage: Optional[str] = None

    # Deprecated: legacy multi-storage fields, kept for backward compatibility.
    # If memory_storage is set, these are ignored.
    summarize_agent_id: Optional[str] = 'memory_summarize_agent'
    memory_storages: Optional[List[str]] = ['ram_memory_storage']
    memory_retrieval_storage: Optional[str] = None

    # Cached resolved storage instance (not serialized)
    _resolved_storage: Optional[MemoryStorage] = None

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.MEMORY, **kwargs)

    # ================================================================
    # Storage resolution
    # ================================================================

    def _resolve_storage(self) -> Optional[MemoryStorage]:
        """Resolve the effective MemoryStorage instance.

        Resolution order:
            1. If ``memory_storage`` is set → look it up from the manager.
            2. Else if legacy ``memory_storages`` is set → build a
               ``LegacyHybridMemoryStorage`` wrapping them.
            3. Otherwise → None.

        The result is cached in ``_resolved_storage`` for the lifetime of
        this Memory instance.  Call ``_invalidate_storage()`` if config changes.

        Returns:
            The resolved MemoryStorage, or None if nothing is configured.
        """
        if self._resolved_storage is not None:
            return self._resolved_storage

        # Path 1: new single-storage field
        if self.memory_storage:
            self._resolved_storage = MemoryStorageManager().get_instance_obj(
                self.memory_storage
            )
            return self._resolved_storage

        # Path 2: legacy multi-storage → wrap in LegacyHybridMemoryStorage
        if self.memory_storages:
            retrieval = self.memory_retrieval_storage or (
                self.memory_storages[0] if self.memory_storages else None
            )
            hybrid = LegacyHybridMemoryStorage()
            hybrid.name = f'_legacy_hybrid_{self.name or "memory"}'
            hybrid.storage_names = list(self.memory_storages)
            hybrid.retrieval_storage_name = retrieval
            self._resolved_storage = hybrid
            return self._resolved_storage

        return None

    def _invalidate_storage(self):
        """Clear cached storage so next access re-resolves."""
        self._resolved_storage = None

    # ================================================================
    # Store
    # ================================================================

    def add(self, message_list: List[Message], session_id: str = None,
            agent_id: str = None, **kwargs) -> None:
        """Persist messages to the configured storage backend."""
        if not message_list:
            return
        storage = self._resolve_storage()
        if storage:
            storage.add(message_list, session_id, agent_id, **kwargs)

    async def async_add(self, message_list: List[Message], session_id: str = None,
                        agent_id: str = None, **kwargs) -> None:
        """Async version of :meth:`add`."""
        if not message_list:
            return
        storage = self._resolve_storage()
        if storage:
            await storage.async_add(message_list, session_id, agent_id, **kwargs)

    # ================================================================
    # Delete
    # ================================================================

    def delete(self, session_id: str = None, **kwargs) -> None:
        """Delete messages from the configured storage backend."""
        storage = self._resolve_storage()
        if storage:
            storage.delete(session_id, **kwargs)

    async def async_delete(self, session_id: str = None, **kwargs) -> None:
        """Async version of :meth:`delete`."""
        storage = self._resolve_storage()
        if storage:
            await storage.async_delete(session_id, **kwargs)

    # ================================================================
    # Retrieve
    # ================================================================

    def get(self, session_id: str = None, agent_id: str = None,
            prune: bool = False, token_budget: int = None,
            **kwargs) -> List[Message]:
        """Retrieve messages from the configured storage.

        Args:
            session_id: The session identifier.
            agent_id: The agent identifier.
            prune: Whether to prune messages to fit token budget.
            token_budget: External token budget override; falls back to
                ``self.max_tokens``.

        Returns:
            List of messages, pruned if requested.
        """
        storage = self._resolve_storage()
        if not storage:
            return []
        memories = storage.get(session_id, agent_id, **kwargs)
        if prune:
            memories = self.prune(memories, token_budget=token_budget)
        return memories

    async def async_get(self, session_id: str = None, agent_id: str = None,
                        prune: bool = False, token_budget: int = None,
                        **kwargs) -> List[Message]:
        """Async version of :meth:`get`."""
        storage = self._resolve_storage()
        if not storage:
            return []
        memories = await storage.async_get(session_id, agent_id, **kwargs)
        if prune:
            memories = await self.async_prune(memories, token_budget=token_budget)
        return memories

    # ================================================================
    # Prune
    # ================================================================

    def prune(self, memories: List[Message], token_budget: int = None) -> List[Message]:
        """Prune messages to fit within a token budget.

        Default strategy: drop oldest messages first, then optionally
        compress the dropped messages into a summary via
        ``memory_compressor``.

        Args:
            memories: The full list of messages.
            token_budget: Max tokens allowed; falls back to ``self.max_tokens``.

        Returns:
            Pruned list of messages within budget.
        """
        if not memories:
            return []

        budget = token_budget or self.max_tokens
        result = memories[:]
        tokens = get_memory_tokens(result, self.agent_llm_name)
        if tokens <= budget:
            return result

        pruned = []
        while result and tokens > budget:
            pruned.append(result.pop(0))
            tokens = get_memory_tokens(result, self.agent_llm_name)

        if pruned and self.memory_compressor:
            compressed = self._compress(pruned, remaining_budget=budget - tokens)
            if compressed:
                result.insert(0, Message(
                    type=ChatMessageEnum.SYSTEM,
                    content=f"[Summary of earlier conversation]\n{compressed}"
                ))

        return result

    async def async_prune(self, memories: List[Message],
                          token_budget: int = None) -> List[Message]:
        """Async version of :meth:`prune`.

        Needed when the memory compressor itself is async (e.g. calls an LLM).
        The pruning logic is identical; only the compress step differs.
        """
        if not memories:
            return []

        budget = token_budget or self.max_tokens
        result = memories[:]
        tokens = get_memory_tokens(result, self.agent_llm_name)
        if tokens <= budget:
            return result

        pruned = []
        while result and tokens > budget:
            pruned.append(result.pop(0))
            tokens = get_memory_tokens(result, self.agent_llm_name)

        if pruned and self.memory_compressor:
            compressed = await self._async_compress(
                pruned, remaining_budget=budget - tokens
            )
            if compressed:
                result.insert(0, Message(
                    type=ChatMessageEnum.SYSTEM,
                    content=f"[Summary of earlier conversation]\n{compressed}"
                ))

        return result

    # ================================================================
    # Build Context — the primary interface for prompt injection
    # ================================================================

    def build_context(self, session_id: str, agent_id: str = None,
                      token_budget: int = None, **kwargs) -> dict:
        """Build the memory context dict to inject into a prompt template.

        This is the main interface the agent / prompt module should call.

        Args:
            session_id: The session identifier.
            agent_id: The agent identifier.
            token_budget: Max tokens for memory content.

        Returns:
            A dict keyed by ``self.memory_key``.
        """
        messages = self.get(
            session_id=session_id, agent_id=agent_id,
            prune=True, token_budget=token_budget, **kwargs
        )
        return {self.memory_key: get_memory_string(messages)}

    async def async_build_context(self, session_id: str, agent_id: str = None,
                                  token_budget: int = None, **kwargs) -> dict:
        """Async version of :meth:`build_context`."""
        messages = await self.async_get(
            session_id=session_id, agent_id=agent_id,
            prune=True, token_budget=token_budget, **kwargs
        )
        return {self.memory_key: get_memory_string(messages)}

    # ================================================================
    # Deprecated — kept for backward compatibility
    # ================================================================

    def summarize_memory(self, session_id: str, agent_id: str = None,
                         **kwargs) -> str:
        """Generate a summary of the conversation memory.

        .. deprecated::
            Use a ``memory_compressor`` instead.
        """
        warnings.warn(
            "summarize_memory() is deprecated and will be removed in a future "
            "version. Configure a memory_compressor instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        messages = self.get(session_id=session_id, agent_id=agent_id, **kwargs)
        summarize_messages = self.get(
            session_id=session_id, agent_id=agent_id, type='summarize'
        )
        summarize_content = (
            summarize_messages[-1].content if summarize_messages else ''
        )
        messages_str = get_memory_string(messages)
        agent = AgentManager().get_instance_obj(self.summarize_agent_id)
        output_object: OutputObject = agent.run(
            input=messages_str, summarize_content=summarize_content
        )
        return output_object.get_data('output')

    async def async_summarize_memory(self, session_id: str, agent_id: str = None,
                                     **kwargs) -> str:
        """Async version of :meth:`summarize_memory`.

        .. deprecated::
            See :meth:`summarize_memory` deprecation notice.
        """
        warnings.warn(
            "async_summarize_memory() is deprecated and will be removed in a "
            "future version. Configure a memory_compressor instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        messages = await self.async_get(
            session_id=session_id, agent_id=agent_id, **kwargs
        )
        summarize_messages = await self.async_get(
            session_id=session_id, agent_id=agent_id, type='summarize'
        )
        summarize_content = (
            summarize_messages[-1].content if summarize_messages else ''
        )
        messages_str = get_memory_string(messages)
        agent = AgentManager().get_instance_obj(self.summarize_agent_id)
        output_object: OutputObject = await agent.async_run(
            input=messages_str, summarize_content=summarize_content
        )
        return output_object.get_data('output')

    # ================================================================
    # Internal helpers
    # ================================================================

    def _compress(self, messages: List[Message], remaining_budget: int) -> Optional[str]:
        """Compress a list of messages using the configured compressor."""
        compressor: MemoryCompressor = MemoryCompressorManager().get_instance_obj(
            self.memory_compressor
        )
        if compressor:
            return compressor.compress_memory(messages, remaining_budget)
        return None

    async def _async_compress(self, messages: List[Message],
                              remaining_budget: int) -> Optional[str]:
        """Async version of :meth:`_compress`."""
        compressor: MemoryCompressor = MemoryCompressorManager().get_instance_obj(
            self.memory_compressor
        )
        if compressor:
            if hasattr(compressor, 'async_compress_memory'):
                return await compressor.async_compress_memory(
                    messages, remaining_budget
                )
            # Fallback to sync if compressor has no async method
            return compressor.compress_memory(messages, remaining_budget)
        return None

    # ================================================================
    # Configuration & Copy
    # ================================================================

    def set_by_agent_model(self, **kwargs) -> 'Memory':
        """Create a copy of this memory with agent-level overrides applied."""
        copied = self.create_copy()
        overridable_fields = ('memory_key', 'max_tokens', 'agent_llm_name')
        for field in overridable_fields:
            val = kwargs.get(field)
            if val is not None:
                setattr(copied, field, val)
        return copied

    def get_instance_code(self) -> str:
        """Return the unique instance code for this memory."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: MemoryConfiger) -> 'Memory':
        """Initialize this memory from a MemoryConfiger object.

        Args:
            component_configer: The MemoryConfiger object.

        Returns:
            Self, after applying configuration.
        """
        field_mapping = {
            'name': 'name',
            'description': 'description',
            'memory_key': 'memory_key',
            'max_tokens': 'max_tokens',
            'memory_compressor': 'memory_compressor',
            'memory_storage': 'memory_storage',
            'memory_storages': 'memory_storages',
            'memory_retrieval_storage': 'memory_retrieval_storage',
        }
        for configer_field, self_field in field_mapping.items():
            value = getattr(component_configer, configer_field, None)
            if value:
                setattr(self, self_field, value)

        if component_configer.type:
            self.type = next(
                (m for m in MemoryTypeEnum if m.value == component_configer.type),
                None,
            )

        # Legacy fallback: if no retrieval storage set, default to first write storage
        if not self.memory_storage and not self.memory_retrieval_storage and self.memory_storages:
            self.memory_retrieval_storage = self.memory_storages[0]

        # Deprecated field — only set if explicitly configured
        if getattr(component_configer, 'memory_summarize_agent', None):
            self.summarize_agent_id = component_configer.memory_summarize_agent

        # Invalidate cached storage so it re-resolves with new config
        self._invalidate_storage()

        return self

    def create_copy(self):
        """Create a shallow copy with mutable collections duplicated."""
        copied = self.model_copy()
        if self.memory_storages is not None:
            copied.memory_storages = self.memory_storages.copy()
        # Clear cached storage on copy — each copy resolves independently
        copied._resolved_storage = None
        return copied