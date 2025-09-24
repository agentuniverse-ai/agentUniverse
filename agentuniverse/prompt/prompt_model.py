# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 19:22
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: prompt_model.py
"""Agent Prompt Model module."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from agentuniverse.agent.memory.enum import ChatMessageEnum


class AgentPromptModel(BaseModel):
    """Agent Prompt Model class."""

    introduction: Optional[str] = None
    target: Optional[str] = None
    instruction: Optional[str] = None
    
    # 使用 Property 确保每次实例化都返回新的字典对象
    @property
    def message_type_mapping(self) -> Dict[str, str]:
        """Get the message type mapping."""
        return {
            'introduction': ChatMessageEnum.SYSTEM.value,
            'target': ChatMessageEnum.SYSTEM.value,
            'instruction': ChatMessageEnum.HUMAN.value
        }

    def __add__(self, other: 'AgentPromptModel') -> 'AgentPromptModel':
        """Merge two objects into one object.
        
        Args:
            other (AgentPromptModel): Another AgentPromptModel instance to merge with.
            
        Returns:
            AgentPromptModel: A new merged AgentPromptModel instance.
        """
        if not isinstance(other, AgentPromptModel):
            return NotImplemented
            
        merged_object = AgentPromptModel()
        all_keys = set(self.model_fields.keys()) | set(other.model_fields.keys())
        for key in all_keys:
            # 获取属性值，优先使用other的值（如果存在且非空）
            other_value = getattr(other, key, None)
            self_value = getattr(self, key, None)
            value = other_value if other_value is not None else self_value
            setattr(merged_object, key, value)
        return merged_object

    def __bool__(self) -> bool:
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
        return self.message_type_mapping.get(attribute_name, ChatMessageEnum.HUMAN.value)
