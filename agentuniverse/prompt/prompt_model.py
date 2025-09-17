# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 19:22
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: prompt_model.py
"""Agent Prompt Model module."""

from typing import Optional

from pydantic import BaseModel

from agentuniverse.agent.memory.enum import ChatMessageEnum


class AgentPromptModel(BaseModel):
    """Agent Prompt Model class."""

    introduction: Optional[str] = None
    target: Optional[str] = None
    instruction: Optional[str] = None
    _message_type_mapping: dict[str, str] = {
        "introduction": ChatMessageEnum.SYSTEM.value,
        "target": ChatMessageEnum.SYSTEM.value,
        "instruction": ChatMessageEnum.HUMAN.value,
    }

    def __add__(self, other):
        """Merge two objects into one object."""
        merged_object = AgentPromptModel()
        for key in set(self.__dict__.keys()).union(other.__dict__.keys()):
            value = getattr(self, key, None)
            if value is None:
                value = getattr(other, key, None)
            setattr(merged_object, key, value)
        return merged_object

    def __bool__(self):
        """Check whether the object is empty.

        Return True if one of the introduction, target and instruction attribute is not empty.
        Return False otherwise.
        """
        return bool(self.introduction or self.target or self.instruction)

    def get_message_type(self, attribute_name: str) -> str:
        """Get the message type of the attribute in the agent prompt model.

        Args:
            attribute_name (str): The name of the attribute.

        Returns:
            str: The message type of the attribute(system/human/ai).
        """
        return self._message_type_mapping.get(attribute_name, ChatMessageEnum.HUMAN.value)
