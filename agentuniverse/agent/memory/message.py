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

# OpenAI 多模态 content part 中合法的 type 值
_OPENAI_CONTENT_PART_TYPES = frozenset({
    "text", "image_url", "input_audio", "file", "refusal",
})


def _is_openai_content_part(item: Any) -> bool:
    """检查单个元素是否符合 OpenAI content part 格式。

    合法的 content part:
    - str（纯文本，openai_normalize_content 会自动包装为 {"type": "text", "text": ...}）
    - dict 且包含 "type" 字段，且 type 值属于已知的 OpenAI content part 类型
    """
    if isinstance(item, str):
        return True
    if isinstance(item, dict):
        return item.get("type") in _OPENAI_CONTENT_PART_TYPES
    return False


def normalize_tool_result(result: Any) -> ContentT:
    """将工具返回值转换为 ContentT，尽量保留多模态内容。

    - None → 空字符串
    - str  → 直接返回
    - list → 如果每个元素都符合 OpenAI 多模态 content part 格式则保留，否则退化为 str
    - 其它 → str(result)
    """
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    if isinstance(result, list) and len(result) > 0:
        if all(_is_openai_content_part(item) for item in result):
            return result
        return str(result)
    return str(result)


def _extract_plain_text(content: Optional[ContentT]) -> str:
    """从 ContentT 中提取纯文本。

    - str  → 直接返回
    - list → 遍历每个 part：
        - str 直接拼接
        - dict 取 "text" 字段（兼容 OpenAI multi-modal content parts 格式）
    - None → 返回空字符串
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts: List[str] = []
    for part in content:
        if isinstance(part, str):
            parts.append(part)
        elif isinstance(part, dict):
            # OpenAI 格式: {"type": "text", "text": "..."} 或直接 {"text": "..."}
            text = part.get("text")
            if text is not None:
                parts.append(str(text))
    return "".join(parts)


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

    # ---- 纯文本便捷属性 ----

    @property
    def content_text(self) -> str:
        """获取 content 的纯文本表示。

        - content 为 str 时直接返回
        - content 为 list 时提取所有文本部分并拼接
        - content 为 None 时返回空字符串
        """
        return _extract_plain_text(self.content)

    @property
    def reasoning_text(self) -> str:
        """获取 reasoning_content 的纯文本表示。

        - reasoning_content 为 str 时直接返回
        - reasoning_content 为 list 时提取所有文本部分并拼接
        - reasoning_content 为 None 时返回空字符串
        """
        return _extract_plain_text(self.reasoning_content)

        # ---- 序列化 / 反序列化 ----

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
