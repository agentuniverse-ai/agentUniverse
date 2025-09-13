# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_output.py
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from agentuniverse.agent.memory.message import Message

LLM_OUTPUT_TYPE = Literal[
    "text",
    "message",
    "function_call",
    "tool_call",
    "stream",
    "error"
]

FINISH_REASON_TYPE = Literal[
    "stop",
    "length",
    "tool_calls",
    "function_call",
    "content_filter",
    "error"
]




class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False
        frozen = True


def prune_none(obj):
    if isinstance(obj, dict):
        return {k: prune_none(v) for k, v in obj.items() if v is not None}

    if isinstance(obj, list):
        return [prune_none(v) for v in obj if v is not None]
    return obj


class TokenUsage(BaseModel):
    # ======== 基础字段 ========
    # 输入
    text_in: int = 0
    image_in: int = 0
    audio_in: int = 0
    cached_in: int = 0

    # 输出
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
        """历史字段别名：所有输出 token 总和"""
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

    # ======== 解析入口 ========
    @classmethod
    def from_openai(cls, usage: Dict[str, Any]) -> "TokenUsage":
        if not usage:
            return cls()
        usage = prune_none(usage)

        # ---------- chat/completions ----------
        if "prompt_tokens" in usage:
            det_in = usage.get("prompt_tokens_details", {})
            det_out = usage.get("completion_tokens_details", {})

            return cls(
                text_in=det_in.get("text_tokens", usage["prompt_tokens"]),
                image_in=det_in.get("image_tokens", 0),
                audio_in=det_in.get("audio_tokens", 0),
                cached_in=det_in.get("cached_tokens", 0),
                text_out=det_out.get("text_tokens", usage["completion_tokens"]),
                image_out=det_out.get("image_tokens", 0),
                audio_out=det_out.get("audio_tokens", 0),
                cached_out=det_out.get("cached_tokens", 0),
                reasoning_out=det_out.get("reasoning_tokens", 0),
            )

        # ---------- image/audio ----------
        if "input_tokens" in usage:
            det_in = usage.get("input_tokens_details", {})
            det_out = usage.get("output_token_details", {})

            return cls(
                text_in=det_in.get("text_tokens", usage["input_tokens"]),
                image_in=det_in.get("image_tokens", 0),
                audio_in=det_in.get("audio_tokens", 0),
                cached_in=det_in.get("cached_tokens", 0),
                text_out=det_out.get("text_tokens", usage["output_tokens"]),
                image_out=det_out.get("image_tokens", 0),
                audio_out=det_out.get("audio_tokens", 0),
                cached_out=det_out.get("cached_tokens", 0),
                reasoning_out=det_out.get("reasoning_tokens", 0),
            )

        # ---------- Realtime ----------
        if "input_tokens" in usage and "output_tokens" in usage:
            return cls(
                text_in=usage.get("input_token_details", {}).get(
                    "text_tokens", usage["input_tokens"]
                ),
                audio_in=usage.get("input_token_details", {}).get("audio_tokens", 0),
                cached_in=usage.get("input_token_details", {}).get("cached_tokens", 0),
                text_out=usage.get("output_token_details", {}).get(
                    "text_tokens", usage["output_tokens"]
                ),
                audio_out=usage.get("output_token_details", {}).get("audio_tokens", 0),
                cached_out=usage.get("output_token_details", {}).get(
                    "cached_tokens", 0
                ),
            )

        return cls()

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
        tmp = self + other
        for field in self.__fields__:
            setattr(self, field, getattr(tmp, field))
        return self

    def to_dict(self, *, keep_zero: bool = False) -> dict:
        def _filter(d: dict) -> dict:
            return d if keep_zero else {k: v for k, v in d.items() if v}

        prompt_details = _filter(
            {
                "text_tokens": self.text_in,
                "image_tokens": self.image_in,
                "audio_tokens": self.audio_in,
                "cached_tokens": self.cached_in,
            }
        )

        completion_details = _filter(
            {
                "text_tokens": self.text_out,
                "image_tokens": self.image_out,
                "audio_tokens": self.audio_out,
                "cached_tokens": self.cached_out,
                "reasoning_tokens": self.reasoning_out,
            }
        )

        data = {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }

        if prompt_details:
            data["prompt_tokens_details"] = prompt_details
        if completion_details:
            data["completion_tokens_details"] = completion_details

        return data



class LLMOutput(BaseModel):
    """The basic class for llm output."""

    type: LLM_OUTPUT_TYPE = "text"

    """The text of the llm output."""
    text: Optional[str] = None

    """The raw data of the llm output."""
    raw: Optional[Any] = None

    message: Optional[Message] = None

    finish_reason: Optional[FINISH_REASON_TYPE] = None

    function_call: Optional[FunctionCall] = None

    usage: Optional[TokenUsage] = None

    def is_stream(self) -> bool:
        return self.type == "stream"

    def is_function_call(self) -> bool:
        return self.type in ("function_call", "tool_call")
