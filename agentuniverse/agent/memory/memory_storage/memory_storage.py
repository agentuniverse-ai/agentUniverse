# !/usr/bin/env python3
# -*- coding:utf-8 -*-

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
    """The basic class for the memory storage.

    Attributes
        name (Optional[str]): The name of the memory storage class.
        description (Optional[str]): The description of the memory storage class.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    component_type: ComponentEnum = ComponentEnum.MEMORY_STORAGE

    def _initialize_by_component_configer(self, memory_storage_config: ComponentConfiger) -> "MemoryStorage":
        """Initialize the MemoryStorage by the ComponentConfiger object.

        Args:
            memory_storage_config(ComponentConfiger): A configer contains memory_storage basic info.
        Returns:
            MemoryStorage: A MemoryStorage instance.
        """
        if getattr(memory_storage_config, "name", None):
            self.name = memory_storage_config.name
        if getattr(memory_storage_config, "description", None):
            self.description = memory_storage_config.description
        return self

    def add(self, message_list: List[Message], session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Add messages to the memory db.

        Args:
            message_list (List[Message]): The list of messages to add.
            session_id (str): The session id of the memory to add.
            agent_id (str): The agent id of the memory to add.
        """
        pass

    def delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Delete the memory from the database.

        Args:
            session_id (str): The session id of the memory to delete.
            agent_id (str): The agent id of the memory to delete.
        """
        pass

    def get(self, session_id: str = None, agent_id: str = None, top_k=10, **kwargs) -> List[Message]:
        """Get messages from the memory db.

        Args:
            session_id (str): The session id of the memory to get.
            agent_id (str): The agent id of the memory to get.
            top_k (int): The number of messages to return.
        Returns:
            List[Message]: A list of aU messages.
        """
        pass

    def create_copy(self):
        return self
