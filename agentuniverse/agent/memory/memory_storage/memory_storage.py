# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
# @Time    : 2024/10/10 18:53
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_storage.py
from typing import Optional, List

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


class MemoryStorage(ComponentBase):
    """The base class for memory storage.

    A MemoryStorage is responsible for the physical persistence and retrieval
    of messages. Each MemoryStorage implementation handles a single storage
    backend (RAM, SQL, vector DB, etc.).

    For hybrid scenarios (multiple backends, mixed retrieval), use
    ``HybridMemoryStorage`` which composes multiple MemoryStorage instances
    behind a single interface.

    Attributes:
        name: The name of the memory storage instance.
        description: A human-readable description.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    component_type: ComponentEnum = ComponentEnum.MEMORY_STORAGE

    def _initialize_by_component_configer(self, memory_storage_config: ComponentConfiger) -> 'MemoryStorage':
        """Initialize the MemoryStorage by the ComponentConfiger object.

        Args:
            memory_storage_config: A configer contains memory_storage basic info.

        Returns:
            A MemoryStorage instance.
        """
        if getattr(memory_storage_config, 'name', None):
            self.name = memory_storage_config.name
        if getattr(memory_storage_config, 'description', None):
            self.description = memory_storage_config.description
        return self

    # ================================================================
    # Synchronous interface
    # ================================================================

    def add(self, message_list: List[Message], session_id: str = None,
            agent_id: str = None, **kwargs) -> None:
        """Add messages to the storage backend.

        Args:
            message_list: The list of messages to add.
            session_id: The session id of the memory to add.
            agent_id: The agent id of the memory to add.
        """
        pass

    def delete(self, session_id: str = None, agent_id: str = None,
               **kwargs) -> None:
        """Delete messages from the storage backend.

        Args:
            session_id: The session id of the memory to delete.
            agent_id: The agent id of the memory to delete.
        """
        pass

    def get(self, session_id: str = None, agent_id: str = None,
            top_k: int = 10, **kwargs) -> List[Message]:
        """Retrieve messages from the storage backend.

        Args:
            session_id: The session id of the memory to get.
            agent_id: The agent id of the memory to get.
            top_k: The maximum number of messages to return.

        Returns:
            A list of messages.
        """
        pass

    # ================================================================
    # Asynchronous interface
    #
    # Default implementations delegate to the sync versions.
    # Subclasses with native async backends (e.g. asyncpg, aioredis)
    # should override these for true non-blocking behavior.
    # ================================================================

    async def async_add(self, message_list: List[Message], session_id: str = None,
                        agent_id: str = None, **kwargs) -> None:
        """Async version of :meth:`add`.

        Default implementation delegates to the synchronous ``add()``.
        Override in subclasses with native async storage backends.
        """
        await asyncio.to_thread(self.add, message_list, session_id, agent_id, **kwargs)

    async def async_delete(self, session_id: str = None, agent_id: str = None,
                           **kwargs) -> None:
        """Async version of :meth:`delete`.

        Default implementation delegates to the synchronous ``delete()``.
        Override in subclasses with native async storage backends.
        """
        await asyncio.to_thread(self.delete, session_id, agent_id, **kwargs)

    async def async_get(self, session_id: str = None, agent_id: str = None,
                        top_k: int = 10, **kwargs) -> List[Message]:
        """Async version of :meth:`get`.

        Default implementation delegates to the synchronous ``get()``.
        Override in subclasses with native async storage backends.
        """
        return await asyncio.to_thread(self.get, session_id, agent_id, top_k=top_k, **kwargs)

    # ================================================================
    # Copy
    # ================================================================

    def create_copy(self):
        return self
