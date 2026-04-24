# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_output.py
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from enum import Enum
from typing import Literal, List, Optional, Dict, Any

from pydantic import BaseModel

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message, ToolCall

FINISH_REASON_TYPE = Literal[
    "stop",
    "length",
    "tool_calls",
    "function_call",
    "content_filter",
    "error"
]


def prune_none(obj):
    if isinstance(obj, dict):
        return {k: prune_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [prune_none(v) for v in obj if v is not None]
    return obj


class TokenUsage(BaseModel):
    # ======== Basic fields. ========
    # Input
    text_in: int = 0
    image_in: int = 0
    audio_in: int = 0
    cached_in: int = 0

    # Output
    text_out: int = 0
    image_out: int = 0
    audio_out: int = 0
    cached_out: int = 0
    reasoning_out: int = 0

    @property
    def prompt_tokens(self) -> int:
        return self.text_in + self.image_in + self.audio_in + self.cached_in

    @property
    def completion_tokens(self) -> int:
        """Historical field alias: Total of all output tokens."""
        return (
            self.text_out
            + self.image_out
            + self.audio_out
            + self.cached_out
            + self.reasoning_out
        )

    @property
    def cached_tokens(self) -> int:
        return self.cached_in + self.cached_out

    @property
    def reasoning_tokens(self) -> int:
        return self.reasoning_out

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @classmethod
    def from_openai(cls, usage: Optional[Dict[str, Any]]) -> "TokenUsage":
        if not usage:
            return cls()
        usage = prune_none(usage)

        # chat/completions 格式
        if "prompt_tokens" in usage:
            det_in = usage.get("prompt_tokens_details") or {}
            det_out = usage.get("completion_tokens_details") or {}
            return cls(
                text_in=det_in.get("text_tokens",
                                   usage.get("prompt_tokens", 0)),
                image_in=det_in.get("image_tokens", 0),
                audio_in=det_in.get("audio_tokens", 0),
                cached_in=det_in.get("cached_tokens", 0),
                text_out=det_out.get("text_tokens",
                                     usage.get("completion_tokens", 0)),
                image_out=det_out.get("image_tokens", 0),
                audio_out=det_out.get("audio_tokens", 0),
                cached_out=det_out.get("cached_tokens", 0),
                reasoning_out=det_out.get("reasoning_tokens", 0),
            )

        if "input_tokens" in usage:
            det_in = usage.get("input_tokens_details") or usage.get(
                "input_token_details") or {}
            det_out = usage.get("output_tokens_details") or usage.get(
                "output_token_details") or {}
            return cls(
                text_in=det_in.get("text_tokens",
                                   usage.get("input_tokens", 0)),
                image_in=det_in.get("image_tokens", 0),
                audio_in=det_in.get("audio_tokens", 0),
                cached_in=det_in.get("cached_tokens", 0),
                text_out=det_out.get("text_tokens",
                                     usage.get("output_tokens", 0)),
                image_out=det_out.get("image_tokens", 0),
                audio_out=det_out.get("audio_tokens", 0),
                cached_out=det_out.get("cached_tokens", 0),
                reasoning_out=det_out.get("reasoning_tokens", 0),
            )

        return cls()

    @classmethod
    def from_anthropic(cls, usage: Optional[Dict[str, Any]]) -> "TokenUsage":
        """解析 Anthropic Messages API 格式的 usage。

        Anthropic usage 字段：
          - input_tokens: 未命中缓存的输入 token（不含 cache_creation 和 cache_read）
          - output_tokens: 输出 token（含 thinking tokens，无单独 reasoning 字段）
          - cache_creation_input_tokens: 写入缓存的 token 总数
          - cache_read_input_tokens: 从缓存读取的 token 数
          - cache_creation: {              # 较新的细分字段
                ephemeral_5m_input_tokens,  # 5min TTL 缓存写入
                ephemeral_1h_input_tokens,  # 1h TTL 缓存写入
            }
          - server_tool_use: { web_search_requests: int }  # 服务端工具

        重要：总输入 = input_tokens + cache_creation_input_tokens + cache_read_input_tokens
        """
        if not usage:
            return cls()

        # cache_creation_input_tokens 是顶层汇总值，
        # 等于 cache_creation.ephemeral_5m + ephemeral_1h 之和，取顶层即可。
        cache_creation = usage.get("cache_creation_input_tokens", 0) or 0
        cache_read = usage.get("cache_read_input_tokens", 0) or 0

        return cls(
            # input_tokens 是扣除缓存后的"纯"输入，
            # 加上 cache_creation 才是实际处理的全部非缓存输入
            text_in=(usage.get("input_tokens", 0) or 0) + cache_creation,
            cached_in=cache_read,
            text_out=usage.get("output_tokens", 0) or 0,
            # Anthropic 目前不单独拆分 reasoning / image / audio output tokens
        )

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        if not isinstance(other, TokenUsage):
            return NotImplemented

        return TokenUsage(
            text_in=self.text_in + other.text_in,
            image_in=self.image_in + other.image_in,
            audio_in=self.audio_in + other.audio_in,
            cached_in=self.cached_in + other.cached_in,
            text_out=self.text_out + other.text_out,
            image_out=self.image_out + other.image_out,
            audio_out=self.audio_out + other.audio_out,
            cached_out=self.cached_out + other.cached_out,
            reasoning_out=self.reasoning_out + other.reasoning_out,
        )

    def __iadd__(self, other: "TokenUsage") -> "TokenUsage":
        if not isinstance(other, TokenUsage):
            return NotImplemented
        self.text_in += other.text_in
        self.image_in += other.image_in
        self.audio_in += other.audio_in
        self.cached_in += other.cached_in
        self.text_out += other.text_out
        self.image_out += other.image_out
        self.audio_out += other.audio_out
        self.cached_out += other.cached_out
        self.reasoning_out += other.reasoning_out
        return self

    def to_dict(self, *, include_zero: bool = False) -> Dict[str, Any]:
        def _filter(d: dict) -> dict:
            return d if include_zero else {k: v for k, v in d.items() if v}

        data: Dict[str, Any] = {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }

        prompt_details = _filter({
            "text_tokens": self.text_in,
            "image_tokens": self.image_in,
            "audio_tokens": self.audio_in,
            "cached_tokens": self.cached_in,
        })
        if prompt_details:
            data["prompt_tokens_details"] = prompt_details

        completion_details = _filter({
            "text_tokens": self.text_out,
            "image_tokens": self.image_out,
            "audio_tokens": self.audio_out,
            "cached_tokens": self.cached_out,
            "reasoning_tokens": self.reasoning_out,
        })
        if completion_details:
            data["completion_tokens_details"] = completion_details

        return data


class LLMOutput(BaseModel):
    raw: Optional[Any] = None
    text: str = ""
    message: Optional[Message] = None

    response_id: Optional[str] = None

    finish_reason: Optional[FINISH_REASON_TYPE] = None

    usage: Optional[TokenUsage] = None

    reasoning_text: Optional[str] = None

    # === 便捷方法 ===
    def has_tool_calls(self) -> bool:
        """是否包含工具调用"""
        return self.message is not None and self.message.has_tool_calls()

    def get_tool_calls(self) -> List[ToolCall]:
        """获取工具调用列表"""
        if self.message and self.message.tool_calls:
            return self.message.tool_calls
        return []

    def is_stop(self) -> bool:
        """是否正常结束"""
        return self.finish_reason == "stop"

    def is_tool_use(self) -> bool:
        """是否因工具调用而结束"""
        return self.finish_reason == "tool_calls"

    def to_dict(self, *, exclude_none: bool = True) -> Dict[str, Any]:
        """转换为字典"""
        data = {
            "text": self.text,
            "response_id": self.response_id,
            "finish_reason": self.finish_reason,
            "reasoning_text": self.reasoning_text,
        }
        if self.message:
            data["message"] = self.message.to_dict()
        if self.usage:
            data["usage"] = self.usage.to_dict()

        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        return data


# ============ 流式处理 ============

class StreamEventType(str, Enum):
    """流式事件类型"""
    TEXT_DELTA = "text.delta"
    REASONING_DELTA = "reasoning.delta"
    TOOL_CALL_DELTA = "tool_call.delta"
    USAGE = "usage"
    DONE = "done"
    ERROR = "error"


class ToolCallDelta(BaseModel):
    """工具调用增量"""
    index: int = 0
    id: Optional[str] = None
    name: Optional[str] = None
    arguments_delta: str = ""


class LLMStreamEvent(BaseModel):
    """流式输出事件"""
    type: StreamEventType

    # Delta 内容
    text_delta: Optional[str] = None
    reasoning_delta: Optional[str] = None
    tool_call_delta: Optional[ToolCallDelta] = None

    # 终态信息
    usage: Optional[TokenUsage] = None
    finish_reason: Optional[FINISH_REASON_TYPE] = None
    response_id: Optional[str] = None
    error: Optional[str] = None

    # Raw thinking blocks (with signatures) for multi-turn passthrough
    thinking_blocks: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def text(cls, delta: str) -> "LLMStreamEvent":
        return cls(type=StreamEventType.TEXT_DELTA, text_delta=delta)

    @classmethod
    def reasoning(cls, delta: str) -> "LLMStreamEvent":
        return cls(type=StreamEventType.REASONING_DELTA, reasoning_delta=delta)

    @classmethod
    def tool_call(cls, delta: ToolCallDelta) -> "LLMStreamEvent":
        return cls(type=StreamEventType.TOOL_CALL_DELTA, tool_call_delta=delta)

    @classmethod
    def done(cls, *, finish_reason: FINISH_REASON_TYPE,
             usage: Optional[TokenUsage] = None,
             response_id: Optional[str] = None,
             thinking_blocks: Optional[List[Dict[str, Any]]] = None) -> "LLMStreamEvent":
        return cls(
            type=StreamEventType.DONE,
            finish_reason=finish_reason,
            usage=usage,
            response_id=response_id,
            thinking_blocks=thinking_blocks or None,
        )

    @classmethod
    def err(cls, message: str) -> "LLMStreamEvent":
        return cls(type=StreamEventType.ERROR, error=message)


class StreamReducer:
    """将流式事件聚合为最终 LLMOutput"""

    def __init__(self):
        self._text_chunks: List[str] = []
        self._reasoning_chunks: List[str] = []
        self._tool_calls: Dict[
            int, Dict[str, Any]] = {}  # index -> {id, name, arguments}
        self._usage: Optional[TokenUsage] = None
        self._finish_reason: Optional[FINISH_REASON_TYPE] = None
        self._response_id: Optional[str] = None
        self._error: Optional[str] = None
        self._thinking_blocks: Optional[List[Dict[str, Any]]] = None

    def feed(self, event: LLMStreamEvent) -> None:
        """处理一个流式事件"""
        match event.type:
            case StreamEventType.TEXT_DELTA:
                if event.text_delta:
                    self._text_chunks.append(event.text_delta)

            case StreamEventType.REASONING_DELTA:
                if event.reasoning_delta:
                    self._reasoning_chunks.append(event.reasoning_delta)

            case StreamEventType.TOOL_CALL_DELTA:
                if event.tool_call_delta:
                    self._handle_tool_call_delta(event.tool_call_delta)

            case StreamEventType.USAGE:
                if event.usage:
                    self._usage = event.usage

            case StreamEventType.DONE:
                self._finish_reason = event.finish_reason
                self._response_id = event.response_id
                if event.usage:
                    self._usage = event.usage
                if event.thinking_blocks:
                    self._thinking_blocks = event.thinking_blocks

            case StreamEventType.ERROR:
                self._error = event.error
                self._finish_reason = "error"

    def _handle_tool_call_delta(self, delta: ToolCallDelta) -> None:
        """处理工具调用增量"""
        idx = delta.index
        if idx not in self._tool_calls:
            self._tool_calls[idx] = {"id": None, "name": "", "arguments": ""}

        tc = self._tool_calls[idx]
        if delta.id:
            tc["id"] = delta.id
        if delta.name:
            tc["name"] = delta.name
        if delta.arguments_delta:
            tc["arguments"] += delta.arguments_delta

    def build(self) -> LLMOutput:
        """构建最终输出"""
        text = "".join(self._text_chunks)
        reasoning = "".join(
            self._reasoning_chunks) if self._reasoning_chunks else None

        # 构建 tool_calls
        tool_calls: Optional[List[ToolCall]] = None
        if self._tool_calls:
            tool_calls = [
                ToolCall.create(
                    id=tc["id"] or f"call_{idx}",
                    name=tc["name"],
                    arguments=tc["arguments"]
                )
                for idx, tc in sorted(self._tool_calls.items())
            ]

        # 构建 Message
        message = Message(
            type=ChatMessageEnum.ASSISTANT,
            content=text or None,
            reasoning_content=reasoning,
            tool_calls=tool_calls,
        )
        # Store thinking blocks (with signatures) for multi-turn passthrough
        if self._thinking_blocks:
            message._thinking_blocks = self._thinking_blocks

        return LLMOutput(
            text=text,
            message=message,
            reasoning_text=reasoning,
            usage=self._usage,
            finish_reason=self._finish_reason,
            response_id=self._response_id,
        )

    @property
    def current_text(self) -> str:
        """获取当前累积的文本"""
        return "".join(self._text_chunks)

    @property
    def has_error(self) -> bool:
        return self._error is not None
