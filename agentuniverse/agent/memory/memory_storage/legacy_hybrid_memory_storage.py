# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: legacy_hybrid_memory_storage.py
"""Backward-compatible hybrid storage that wraps the legacy multi-storage pattern.

When a Memory is configured with the deprecated ``memory_storages`` (list) and
``memory_retrieval_storage`` fields instead of the new singular ``memory_storage``
field, the Memory class auto-constructs a ``HybridMemoryStorage`` to maintain
the same runtime behavior behind a single MemoryStorage interface.

Write operations fan out to *all* child storages.
Read operations go through the designated retrieval storage only.
"""

from typing import Optional, List

from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.memory_storage.memory_storage_manager import MemoryStorageManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class LegacyHybridMemoryStorage(MemoryStorage):
    """A composite MemoryStorage that fans out writes and routes reads.

    Can be used in two ways:
        1. **Programmatic** — constructed by ``Memory._resolve_storage()``
           when legacy ``memory_storages`` / ``memory_retrieval_storage``
           fields are detected.
        2. **YAML-configured** — registered as a normal component and
           initialized via ``_initialize_by_component_configer()``.

    YAML example::

        name: 'my_hybrid_storage'
        description: 'hybrid storage with ram + vector'
        storage_names:
          - ram_memory_storage
          - vector_memory_storage
        retrieval_storage_name: vector_memory_storage
        metadata:
          type: 'MEMORY_STORAGE'
          module: agentuniverse.agent.memory.memory_storage.hybrid_memory_storage
          class: HybridMemoryStorage

    Attributes:
        storage_names: List of storage instance names for write fan-out.
        retrieval_storage_name: The storage instance name used for reads.
            Defaults to the first entry in ``storage_names`` if not set.
    """

    storage_names: Optional[List[str]] = []
    retrieval_storage_name: Optional[str] = None

    def _initialize_by_component_configer(self, memory_storage_config: ComponentConfiger) -> 'LegacyHybridMemoryStorage':
        """Initialize from a ComponentConfiger (YAML-driven).

        Args:
            memory_storage_config: A configer with hybrid storage fields.

        Returns:
            Self, after applying configuration.
        """
        super()._initialize_by_component_configer(memory_storage_config)
        if getattr(memory_storage_config, 'storage_names', None):
            self.storage_names = memory_storage_config.storage_names
        if getattr(memory_storage_config, 'retrieval_storage_name', None):
            self.retrieval_storage_name = memory_storage_config.retrieval_storage_name
        # Default retrieval to first write storage if not explicitly set
        if not self.retrieval_storage_name and self.storage_names:
            self.retrieval_storage_name = self.storage_names[0]
        return self

    # ================================================================
    # Internal helpers
    # ================================================================

    def _iter_write_storages(self):
        """Yield resolved MemoryStorage instances for all write targets."""
        for name in self.storage_names:
            storage = MemoryStorageManager().get_instance_obj(name)
            if storage:
                yield storage

    def _get_read_storage(self) -> Optional[MemoryStorage]:
        """Resolve and return the retrieval storage instance."""
        if not self.retrieval_storage_name:
            return None
        return MemoryStorageManager().get_instance_obj(self.retrieval_storage_name)

    # ================================================================
    # Synchronous interface
    # ================================================================

    def add(self, message_list: List[Message], session_id: str = None,
            agent_id: str = None, **kwargs) -> None:
        """Fan out add to all child storages."""
        if not message_list:
            return
        for storage in self._iter_write_storages():
            storage.add(message_list, session_id, agent_id, **kwargs)

    def delete(self, session_id: str = None, agent_id: str = None,
               **kwargs) -> None:
        """Fan out delete to all child storages."""
        for storage in self._iter_write_storages():
            storage.delete(session_id, agent_id, **kwargs)

    def get(self, session_id: str = None, agent_id: str = None,
            top_k: int = 10, **kwargs) -> List[Message]:
        """Read from the designated retrieval storage only."""
        storage = self._get_read_storage()
        if not storage:
            return []
        return storage.get(session_id, agent_id, top_k=top_k, **kwargs)

    # ================================================================
    # Asynchronous interface
    # ================================================================

    async def async_add(self, message_list: List[Message], session_id: str = None,
                        agent_id: str = None, **kwargs) -> None:
        """Async fan out add to all child storages."""
        if not message_list:
            return
        for storage in self._iter_write_storages():
            await storage.async_add(message_list, session_id, agent_id, **kwargs)

    async def async_delete(self, session_id: str = None, agent_id: str = None,
                           **kwargs) -> None:
        """Async fan out delete to all child storages."""
        for storage in self._iter_write_storages():
            await storage.async_delete(session_id, agent_id, **kwargs)

    async def async_get(self, session_id: str = None, agent_id: str = None,
                        top_k: int = 10, **kwargs) -> List[Message]:
        """Async read from the designated retrieval storage only."""
        storage = self._get_read_storage()
        if not storage:
            return []
        return await storage.async_get(session_id, agent_id, top_k=top_k, **kwargs)