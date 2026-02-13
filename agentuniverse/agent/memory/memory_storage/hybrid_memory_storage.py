# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/12 16:25
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: hybrid_memory_storage.py
"""Composite memory storage that delegates to multiple sub-storages.

``HybridMemoryStorage`` is the user-facing base: it holds a list of child
storage names and delegates every CRUD operation to *all* of them uniformly.
This is the recommended way for users to configure a multi-backend storage
(e.g. vector + KV) behind a single ``memory_storage`` field in Memory.

``LegacyHybridMemoryStorage`` is a backward-compatible subclass auto-created
by ``Memory._resolve_storage()`` when the deprecated ``memory_storages`` +
``memory_retrieval_storage`` fields are detected.  It fans out writes to all
children but routes reads through a single designated retrieval storage.
"""

from typing import Optional, List

from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import MemoryStorageManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class HybridMemoryStorage(MemoryStorage):
    """A composite MemoryStorage that delegates all operations to sub-storages.

    Every CRUD method (add / delete / get) is fanned out to *all* child
    storages.  For ``get``, results from the first storage that returns
    a non-empty list are used (override for custom merge/rerank logic).

    Can be configured via YAML::

        name: 'my_hybrid_storage'
        description: 'vector + kv hybrid'
        storage_names:
          - vector_memory_storage
          - kv_memory_storage
        metadata:
          type: 'MEMORY_STORAGE'
          module: agentuniverse.agent.memory.memory_storage.hybrid_memory_storage
          class: HybridMemoryStorage

    Attributes:
        storage_names: List of child storage instance names.
    """

    storage_names: Optional[List[str]] = []

    def _initialize_by_component_configer(self, memory_storage_config: ComponentConfiger) -> 'HybridMemoryStorage':
        """Initialize from a ComponentConfiger (YAML-driven).

        Args:
            memory_storage_config: A configer with hybrid storage fields.

        Returns:
            Self, after applying configuration.
        """
        super()._initialize_by_component_configer(memory_storage_config)
        if getattr(memory_storage_config, 'storage_names', None):
            self.storage_names = memory_storage_config.storage_names
        return self

    # ================================================================
    # Internal helpers
    # ================================================================

    def _iter_storages(self):
        """Yield resolved MemoryStorage instances for all child storages."""
        for name in (self.storage_names or []):
            storage = MemoryStorageManager().get_instance_obj(name)
            if storage:
                yield storage

    # ================================================================
    # Synchronous interface
    # ================================================================

    def add(self, message_list: List[Message], session_id: str = None,
            agent_id: str = None, **kwargs) -> None:
        """Fan out add to all child storages."""
        if not message_list:
            return
        for storage in self._iter_storages():
            storage.add(message_list, session_id, agent_id, **kwargs)

    def delete(self, session_id: str = None, agent_id: str = None,
               **kwargs) -> None:
        """Fan out delete to all child storages."""
        for storage in self._iter_storages():
            storage.delete(session_id, agent_id, **kwargs)

    def get(self, session_id: str = None, agent_id: str = None,
            top_k: int = 10, **kwargs) -> List[Message]:
        """Get from all child storages; return first non-empty result.

        Override this in subclasses to implement custom merge / rerank
        strategies across multiple backends.
        """
        for storage in self._iter_storages():
            result = storage.get(session_id, agent_id, top_k=top_k, **kwargs)
            if result:
                return result
        return []

    # ================================================================
    # Asynchronous interface
    # ================================================================

    async def async_add(self, message_list: List[Message], session_id: str = None,
                        agent_id: str = None, **kwargs) -> None:
        """Async fan out add to all child storages."""
        if not message_list:
            return
        for storage in self._iter_storages():
            await storage.async_add(message_list, session_id, agent_id, **kwargs)

    async def async_delete(self, session_id: str = None, agent_id: str = None,
                           **kwargs) -> None:
        """Async fan out delete to all child storages."""
        for storage in self._iter_storages():
            await storage.async_delete(session_id, agent_id, **kwargs)

    async def async_get(self, session_id: str = None, agent_id: str = None,
                        top_k: int = 10, **kwargs) -> List[Message]:
        """Async get from all child storages; return first non-empty result."""
        for storage in self._iter_storages():
            result = await storage.async_get(session_id, agent_id, top_k=top_k, **kwargs)
            if result:
                return result
        return []


class LegacyHybridMemoryStorage(HybridMemoryStorage):
    """Backward-compatible hybrid that separates write targets from read target.

    Writes fan out to all ``storage_names`` (inherited from parent).
    Reads go through ``retrieval_storage_name`` only.

    This class is NOT meant to be configured via YAML by users. It is
    auto-constructed by ``Memory._resolve_storage()`` when legacy
    ``memory_storages`` + ``memory_retrieval_storage`` fields are detected.

    Attributes:
        retrieval_storage_name: The storage instance name used for reads.
            Defaults to the first entry in ``storage_names`` if not set.
    """

    retrieval_storage_name: Optional[str] = None

    def _get_read_storage(self) -> Optional[MemoryStorage]:
        """Resolve and return the designated retrieval storage."""
        if not self.retrieval_storage_name:
            return None
        return MemoryStorageManager().get_instance_obj(self.retrieval_storage_name)

    # ================================================================
    # Override reads to go through retrieval storage only
    # ================================================================

    def get(self, session_id: str = None, agent_id: str = None,
            top_k: int = 10, **kwargs) -> List[Message]:
        """Read from the designated retrieval storage only."""
        storage = self._get_read_storage()
        if not storage:
            return []
        return storage.get(session_id, agent_id, top_k=top_k, **kwargs)

    async def async_get(self, session_id: str = None, agent_id: str = None,
                        top_k: int = 10, **kwargs) -> List[Message]:
        """Async read from the designated retrieval storage only."""
        storage = self._get_read_storage()
        if not storage:
            return []
        return await storage.async_get(session_id, agent_id, top_k=top_k, **kwargs)
