# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/11 17:49
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: ram_memory_storage.py
from typing import Optional, List, Dict

from agentuniverse.agent.memory.memory_storage.memory_storage import MemoryStorage
from agentuniverse.agent.memory.message import Message


class RamMemoryStorage(MemoryStorage):
    """The ram memory storage class.

    Attributes:
        messages (dict[str, dict[str, list[Message]]]): The messages in the ram memory.
    """

    messages: Optional[Dict[str, Dict[str, List[Message]]]] = dict()

    def add(self, message_list: List[Message], session_id: str = '', agent_id: str = '', **kwargs) -> None:
        """Add messages to the memory db.

        Args:
            message_list (List[Message]): The list of messages to add.
            session_id (str): The session id of the memory to add.
            agent_id (str): The agent id of the memory to add.
        """
        if not message_list:
            return
        session = self.messages.setdefault(session_id, {})
        agent_messages = session.setdefault(agent_id, [])
        agent_messages.extend(message_list)

    def delete(self, session_id: str = None, agent_id: str = None, **kwargs) -> None:
        """Delete the memory from the database.

        Args:
            session_id (str): The session id of the memory to delete.
            agent_id (str): The agent id of the memory to delete.
        """
        if session_id is not None:
            if agent_id is None:
                self.messages.pop(session_id, None)
            else:
                self.messages.get(session_id, {}).pop(agent_id, None)

    def get(self, session_id: str = '', agent_id: str = '', top_k=10, **kwargs) -> \
            List[Message]:
        """Get messages from the memory db.

        Args:
            session_id (str): The session id of the memory to get.
            agent_id (str): The agent id of the memory to get.
            top_k (int): The number of messages to get.
            **kwargs: Optional ``type`` string or list of message types. Filter
                before selecting the latest top_k matches. None leaves types
                unrestricted; an empty list matches nothing.

        Returns:
            List[Message]: The list of aU messages.
        """
        if top_k <= 0:
            return []
        memories = self.messages.get(session_id, {}).get(agent_id, [])
        message_types = kwargs.get('type')
        if message_types is not None:
            if isinstance(message_types, str):
                message_types = [message_types]
            elif not isinstance(message_types, list):
                raise ValueError("type must be a list or str")
            memories = [message for message in memories if message.type in message_types]
        return memories[-top_k:]
