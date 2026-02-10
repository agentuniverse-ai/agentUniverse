# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 11:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message.py
from typing import Optional, List, Union, Dict, Any, Literal

from pydantic import BaseModel, ConfigDict

from agentuniverse.agent.memory.enum import ChatMessageEnum

ContentT = Union[str, List[Union[str, Dict[str, Any]]]]


class FunctionCall(BaseModel):
    """函数调用详情"""
    name: str
    arguments: str  # JSON 字符串

    def parse_arguments(self) -> Dict[str, Any]:
        import json
        return json.loads(self.arguments)


class ToolCall(BaseModel):
    """工具调用，对标 OpenAI tool_calls 格式"""
    id: str
    type: Literal["function"] = "function"
    function: FunctionCall

    @classmethod
    def create(cls, id: str, name: str,
               arguments: Union[str, Dict]) -> "ToolCall":
        import json
        if isinstance(arguments, dict):
            arguments = json.dumps(arguments, ensure_ascii=False)
        return cls(id=id,
                   function=FunctionCall(name=name, arguments=arguments))


class Message(BaseModel):
    """The basic class for memory message.

    Attributes:
        id (int): The id of the message.
        type (Optional[str]): The type of the message.
        content (Optional[str]): The content of the message.
        source (Optional[str]): The source of the message.
        metadata (Optional[dict]): The metadata of the message.
    """
    type: Optional[ChatMessageEnum] = None
    content: Optional[ContentT] = None
    reasoning_content: Optional[ContentT] = None
    refusal: Optional[str] = None

    # Tool call or function call
    function_call: Optional[FunctionCall] = None  # deprecated，兼容旧代码
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

    # Metadata
    id: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[dict] = None

    model_config = ConfigDict(
        use_enum_values=True,
        extra='allow'
    )

    def to_dict(self, *, include_none: bool = False) -> dict:
        return self.model_dump(exclude_none=not include_none)

    @classmethod
    def from_dict(cls, d: dict) -> "Message":
        if "type" not in d and "role" in d:
            d = {**d, "type": d.pop("role")}
        return cls.model_validate(d)


    def get_extra_fields(self) -> Dict[str, Any]:
        defined_fields = set(self.model_fields.keys())
        all_fields = set(self.__dict__.keys())
        extra_field_names = all_fields - defined_fields
        return {name: getattr(self, name) for name in extra_field_names}

    def has_tool_calls(self) -> bool:
        """是否包含工具调用"""
        return bool(self.tool_calls) or bool(self.function_call)
