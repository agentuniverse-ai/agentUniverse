# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 17:49
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: claude_llm.py
from typing import Any, Optional, AsyncIterator, Iterator, Union, List, Dict

import anthropic
import httpx
from pydantic import Field

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message, ToolCall
from agentuniverse.base.config.component_configer.configers.llm_configer import \
    LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import (
    LLMOutput,
    TokenUsage,
    LLMStreamEvent,
    ToolCallDelta,
)

__all__ = ["ClaudeLLM"]

# ── Max context length lookup ──────────────────────────────────────────
CLAUDE_MAX_CONTEXT_LENGTH: Dict[str, int] = {
    "claude-3-haiku-20240307": 200_000,
    "claude-3-sonnet-20240229": 200_000,
    "claude-3-opus-20240229": 200_000,
    "claude-3-5-sonnet-20240620": 200_000,
    "claude-3-5-sonnet-20241022": 200_000,
    "claude-3-5-haiku-20241022": 200_000,
    "claude-sonnet-4-20250514": 200_000,
    "claude-opus-4-20250514": 200_000,
}


# ── Message conversion helpers ─────────────────────────────────────────

def _enum_to_role(v: Any) -> str:
    """Map ChatMessageEnum (or string) to Anthropic role."""
    s = v.value if hasattr(v, "value") else v
    s = str(s).lower() if s is not None else ""
    if s in ("human", "user"):
        return "user"
    if s in ("ai", "assistant"):
        return "assistant"
    # Anthropic doesn't have "tool" role; tool results are user-turn content blocks.
    return "user"


def _convert_openai_tool_choice_to_anthropic(
        tool_choice: Any,
) -> Dict[str, Any]:
    """Convert OpenAI tool_choice to Anthropic tool_choice.

    OpenAI formats:
      "auto"                          → {"type": "auto"}
      "none"                          → (don't pass tools at all)
      "required"                      → {"type": "any"}
      {"type": "function", "function": {"name": "xxx"}} → {"type": "tool", "name": "xxx"}
    """
    if isinstance(tool_choice, str):
        if tool_choice == "auto":
            return {"type": "auto"}
        elif tool_choice == "required":
            return {"type": "any"}
        elif tool_choice == "none":
            # Anthropic 没有 "none"，需要在调用方移除 tools
            return {"type": "auto"}
        else:
            return {"type": "auto"}
    elif isinstance(tool_choice, dict):
        func = tool_choice.get("function", {})
        name = func.get("name", "")
        if name:
            return {"type": "tool", "name": name}
        return {"type": "auto"}
    return {"type": "auto"}


def _convert_openai_tools_to_anthropic(
        tools: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convert OpenAI-format tools list to Anthropic-format tools list.

    OpenAI:
      {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}

    Anthropic:
      {"name": ..., "description": ..., "input_schema": ...}
    """
    anthropic_tools: List[Dict[str, Any]] = []
    for tool in tools:
        if isinstance(tool, dict) and tool.get("type") == "function":
            func = tool.get("function", {})
            anthropic_tool: Dict[str, Any] = {
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "input_schema": func.get("parameters",
                                         {"type": "object", "properties": {}}),
            }
            anthropic_tools.append(anthropic_tool)
        elif isinstance(tool,
                        dict) and "name" in tool and "input_schema" in tool:
            # Already Anthropic format, pass through
            anthropic_tools.append(tool)
        else:
            # Unknown format, pass through and let API validate
            anthropic_tools.append(tool)
    return anthropic_tools


# ── Content block conversion ──────────────────────────────────────────

def _convert_image_block(block: dict) -> dict:
    """Convert an OpenAI ``image_url`` content block to Anthropic ``image``."""
    img_info = block.get("image_url") or {}
    url = img_info.get("url", "")
    if url.startswith("data:"):
        # data:image/png;base64,<data>
        meta, b64_data = url.split(",", 1)
        media_type = meta.split(":")[1].split(";")[0]
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": b64_data,
            },
        }
    return {
        "type": "image",
        "source": {"type": "url", "url": url},
    }


def _convert_content_blocks(content: Any) -> Any:
    """Convert content (str or list) from OpenAI to Anthropic format.

    Handles ``image_url`` → ``image`` conversion for content block lists.
    Strings are returned unchanged.
    """
    if not isinstance(content, list):
        return content
    result = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "image_url":
            result.append(_convert_image_block(block))
        else:
            result.append(block)
    return result


# ── Main message conversion ───────────────────────────────────────────

def au_messages_to_anthropic(
    messages: List[Any],
) -> tuple[Optional[str], List[Dict[str, Any]]]:
    """Convert agentUniverse Message list → (system_prompt, anthropic_messages).

    Anthropic API differences from OpenAI:
      - system is a top-level parameter, NOT a message.
      - tool results are sent as user-role content blocks with type=tool_result.
      - tool calls (assistant) are content blocks with type=tool_use.
      - image_url content blocks are converted to Anthropic image blocks.
      - thinking blocks from previous assistant turns are preserved.
    """
    system_prompt: Optional[str] = None
    out: List[Dict[str, Any]] = []

    for m in messages or []:
        # ── already a raw dict ──
        if isinstance(m, dict) and "role" in m:
            role = m["role"]
            if role == "system":
                # Merge all system messages into one string.
                text = m.get("content", "")
                system_prompt = (
                    f"{system_prompt}\n{text}" if system_prompt else text
                )
                continue
            # tool-result message (OpenAI format → Anthropic format)
            if role == "tool":
                out.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": m.get("tool_call_id", ""),
                            "content": _convert_content_blocks(
                                m.get("content", "")),
                        }
                    ],
                })
                continue
            # Other raw dict: convert image blocks in content
            converted = dict(m)
            converted["content"] = _convert_content_blocks(m.get("content", ""))
            out.append(converted)
            continue

        # ── typed Message object ──
        msg_type = getattr(m, "type", None) or getattr(m, "role", None)
        role = _enum_to_role(msg_type)
        raw_type = (
            msg_type.value if hasattr(msg_type, "value") else str(msg_type or "")
        ).lower()

        # System message → top-level param
        if raw_type in ("system",):
            text = getattr(m, "content", "") or ""
            if isinstance(text, list):
                text = "\n".join(
                    b.get("text", "") if isinstance(b, dict) else str(b)
                    for b in text
                )
            system_prompt = (
                f"{system_prompt}\n{text}" if system_prompt else text
            )
            continue

        # Tool-result message
        if raw_type in ("tool",) or getattr(m, "tool_call_id", None):
            raw_content = getattr(m, "content", "") or ""
            out.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": getattr(m, "tool_call_id", "") or "",
                        "content": _convert_content_blocks(raw_content),
                    }
                ],
            })
            continue

        # ── Build content blocks ──
        content_blocks: List[Any] = []

        # Prepend thinking blocks for assistant messages (multi-turn thinking)
        thinking_blocks = getattr(m, "_thinking_blocks", None)
        if thinking_blocks and role == "assistant":
            content_blocks.extend(thinking_blocks)

        raw_content = getattr(m, "content", None)

        if raw_content is not None:
            if isinstance(raw_content, str):
                content_blocks.append({"type": "text", "text": raw_content})
            elif isinstance(raw_content, list):
                for block in raw_content:
                    if isinstance(block, str):
                        content_blocks.append({"type": "text", "text": block})
                    elif isinstance(block, dict):
                        if block.get("type") == "image_url":
                            content_blocks.append(_convert_image_block(block))
                        else:
                            content_blocks.append(block)
                    else:
                        content_blocks.append(
                            {"type": "text", "text": str(block)}
                        )

        # Assistant tool_calls → tool_use content blocks
        tool_calls = getattr(m, "tool_calls", None)
        if tool_calls:
            import json as _json

            for tc in tool_calls:
                tc_d = (
                    tc.model_dump()
                    if hasattr(tc, "model_dump")
                    else (tc.dict() if hasattr(tc, "dict") else tc)
                )
                fn = tc_d.get("function") or {}
                args_raw = fn.get("arguments", "{}")
                try:
                    input_obj = (
                        _json.loads(args_raw)
                        if isinstance(args_raw, str)
                        else args_raw
                    )
                except _json.JSONDecodeError:
                    input_obj = {"raw": args_raw}
                content_blocks.append(
                    {
                        "type": "tool_use",
                        "id": tc_d.get("id", ""),
                        "name": fn.get("name", ""),
                        "input": input_obj,
                    }
                )

        item: Dict[str, Any] = {"role": role}
        # Anthropic requires content; for assistant messages with only tool_use
        # blocks, content_blocks already contains them.
        if content_blocks:
            # Simplify: if single text block, use plain string
            if (
                len(content_blocks) == 1
                and isinstance(content_blocks[0], dict)
                and content_blocks[0].get("type") == "text"
            ):
                item["content"] = content_blocks[0]["text"]
            else:
                item["content"] = content_blocks
        else:
            item["content"] = ""

        out.append(item)

    return system_prompt, out


# ── Main class ─────────────────────────────────────────────────────────


class ClaudeLLM(LLM):
    """Anthropic Claude Messages API wrapper.

    - Non-streaming: returns ``LLMOutput``
    - Streaming: yields ``LLMStreamEvent``
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("ANTHROPIC_API_KEY")
    )
    api_url: Optional[str] = Field(
        default_factory=lambda: get_from_env("ANTHROPIC_API_URL")
    )
    proxy: Optional[str] = Field(
        default_factory=lambda: get_from_env("ANTHROPIC_PROXY")
    )
    connection_pool_limits: Optional[int] = None
    ext_params: Optional[dict] = {}

    # ── Client builders ────────────────────────────────────────────────

    def _new_client(self) -> anthropic.Anthropic:
        if self.client is not None:
            return self.client
        return anthropic.Anthropic(
            api_key=self.api_key,
            base_url=self.api_url,
            timeout=self.request_timeout or 60,
            max_retries=self.max_retries or 2,
            http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,
        )

    def _new_async_client(self) -> anthropic.AsyncAnthropic:
        if self.async_client is not None:
            return self.async_client
        return anthropic.AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.api_url,
            timeout=self.request_timeout or 60,
            max_retries=self.max_retries or 2,
            http_client=(
                httpx.AsyncClient(proxy=self.proxy) if self.proxy else None
            ),
        )

    # ── Response parsing helpers ───────────────────────────────────────

    @staticmethod
    def _to_dict(obj: Any) -> dict:
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return dict(obj)

    @staticmethod
    def _extract_thinking_blocks(content_blocks: List[dict]) -> List[dict]:
        """Extract raw thinking blocks (with signature) from content."""
        blocks = []
        for b in content_blocks:
            if b.get("type") == "thinking" and b.get("signature"):
                blocks.append({
                    "type": "thinking",
                    "thinking": b.get("thinking", ""),
                    "signature": b["signature"],
                })
        return blocks

    def _build_llm_output(self, response: Any) -> LLMOutput:
        """Build LLMOutput from a non-streaming Anthropic response."""
        raw = self._to_dict(response)
        content_blocks = raw.get("content") or []

        text_parts: List[str] = []
        tool_calls: List[ToolCall] = []

        for block in content_blocks:
            block_type = block.get("type", "")

            if block_type == "text":
                text_parts.append(block.get("text", ""))

            elif block_type == "thinking":
                # Extended thinking (reasoning) — handled below
                pass

            elif block_type == "tool_use":
                import json as _json

                input_obj = block.get("input", {})
                args_str = (
                    _json.dumps(input_obj, ensure_ascii=False)
                    if isinstance(input_obj, dict)
                    else str(input_obj)
                )
                tool_calls.append(
                    ToolCall.create(
                        id=block.get("id", ""),
                        name=block.get("name", ""),
                        arguments=args_str,
                    )
                )

        text = "".join(text_parts)

        # Reasoning / thinking text
        reasoning_text = None
        thinking_parts = [
            b.get("thinking", "")
            for b in content_blocks
            if b.get("type") == "thinking"
        ]
        if thinking_parts:
            reasoning_text = "".join(thinking_parts)

        # Preserve raw thinking blocks (with signatures) for multi-turn passthrough
        thinking_blocks = self._extract_thinking_blocks(content_blocks)

        # Finish reason mapping
        stop_reason = raw.get("stop_reason", "stop")
        finish_reason = self._map_stop_reason(stop_reason)

        # Usage
        usage = TokenUsage.from_anthropic(raw.get("usage"))

        message = Message(
            type=ChatMessageEnum.ASSISTANT,
            content=text or None,
            reasoning_content=reasoning_text,
            tool_calls=tool_calls or None,
        )
        # Store thinking blocks as extra field (Message allows extra='allow')
        if thinking_blocks:
            message._thinking_blocks = thinking_blocks

        return LLMOutput(
            raw=raw,
            text=text,
            message=message,
            response_id=raw.get("id"),
            finish_reason=finish_reason,
            usage=usage,
            reasoning_text=reasoning_text,
        )

    @staticmethod
    def _map_stop_reason(stop_reason: Optional[str]) -> str:
        """Map Anthropic stop_reason to unified FINISH_REASON_TYPE."""
        mapping = {
            "end_turn": "stop",
            "stop_sequence": "stop",
            "max_tokens": "length",
            "tool_use": "tool_calls",
        }
        return mapping.get(stop_reason or "", stop_reason or "stop")

    # ── Streaming event generators ─────────────────────────────────────

    def _iter_stream_events(
        self, raw_stream: Any
    ) -> Iterator[LLMStreamEvent]:
        """Convert Anthropic streaming events → LLMStreamEvent sequence.

        Anthropic stream event types:
          message_start        → contains input token usage
          content_block_start  → start of text / tool_use / thinking block
          content_block_delta  → incremental content (text, thinking, signature, input_json)
          content_block_stop   → block finished
          message_delta        → stop_reason, output token usage
          message_stop         → final signal
        """
        response_id: Optional[str] = None
        # Track which content block index is which type
        block_types: Dict[int, str] = {}
        # Track tool_use block metadata (id, name) by index
        tool_use_meta: Dict[int, Dict[str, str]] = {}
        # For accumulating usage across message_start and message_delta
        usage_acc: Dict[str, int] = {}
        # Accumulate thinking blocks (text + signature) for multi-turn passthrough
        thinking_acc: Dict[int, Dict[str, str]] = {}

        try:
            with raw_stream as stream:
                for event in stream:
                    ev = self._to_dict(event)
                    ev_type = ev.get("type", "")

                    if ev_type == "message_start":
                        msg = ev.get("message") or {}
                        response_id = msg.get("id")
                        msg_usage = msg.get("usage") or {}
                        usage_acc.update(msg_usage)

                    elif ev_type == "content_block_start":
                        idx = ev.get("index", 0)
                        cb = ev.get("content_block") or {}
                        btype = cb.get("type", "text")
                        block_types[idx] = btype

                        if btype == "tool_use":
                            tool_use_meta[idx] = {
                                "id": cb.get("id", ""),
                                "name": cb.get("name", ""),
                            }
                            # Emit tool_call start event with id + name
                            yield LLMStreamEvent.tool_call(
                                ToolCallDelta(
                                    index=idx,
                                    id=cb.get("id"),
                                    name=cb.get("name"),
                                    arguments_delta="",
                                )
                            )
                        elif btype == "thinking":
                            thinking_acc[idx] = {"thinking": "", "signature": ""}

                    elif ev_type == "content_block_delta":
                        idx = ev.get("index", 0)
                        delta = ev.get("delta") or {}
                        delta_type = delta.get("type", "")

                        if delta_type == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                yield LLMStreamEvent.text(text)

                        elif delta_type == "thinking_delta":
                            thinking = delta.get("thinking", "")
                            if thinking:
                                yield LLMStreamEvent.reasoning(thinking)
                                if idx in thinking_acc:
                                    thinking_acc[idx]["thinking"] += thinking

                        elif delta_type == "signature_delta":
                            sig = delta.get("signature", "")
                            if sig and idx in thinking_acc:
                                thinking_acc[idx]["signature"] = sig

                        elif delta_type == "input_json_delta":
                            # Tool use argument streaming
                            partial = delta.get("partial_json", "")
                            if partial:
                                yield LLMStreamEvent.tool_call(
                                    ToolCallDelta(
                                        index=idx,
                                        id=None,
                                        name=None,
                                        arguments_delta=partial,
                                    )
                                )

                    elif ev_type == "message_delta":
                        delta = ev.get("delta") or {}
                        stop_reason = delta.get("stop_reason")
                        msg_usage = ev.get("usage") or {}
                        usage_acc.update(msg_usage)

                        usage_obj = (
                            TokenUsage.from_anthropic(usage_acc)
                            if usage_acc
                            else None
                        )
                        yield LLMStreamEvent.done(
                            finish_reason=self._map_stop_reason(stop_reason),
                            usage=usage_obj,
                            response_id=response_id,
                            thinking_blocks=self._build_thinking_from_acc(thinking_acc),
                        )

                    # message_stop / content_block_stop — no action needed

        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    async def _aiter_stream_events(
        self, raw_stream: Any
    ) -> AsyncIterator[LLMStreamEvent]:
        """Async version of _iter_stream_events."""
        response_id: Optional[str] = None
        block_types: Dict[int, str] = {}
        tool_use_meta: Dict[int, Dict[str, str]] = {}
        usage_acc: Dict[str, int] = {}
        thinking_acc: Dict[int, Dict[str, str]] = {}

        try:
            async with raw_stream as stream:
                async for event in stream:
                    ev = self._to_dict(event)
                    ev_type = ev.get("type", "")

                    if ev_type == "message_start":
                        msg = ev.get("message") or {}
                        response_id = msg.get("id")
                        msg_usage = msg.get("usage") or {}
                        usage_acc.update(msg_usage)

                    elif ev_type == "content_block_start":
                        idx = ev.get("index", 0)
                        cb = ev.get("content_block") or {}
                        btype = cb.get("type", "text")
                        block_types[idx] = btype

                        if btype == "tool_use":
                            tool_use_meta[idx] = {
                                "id": cb.get("id", ""),
                                "name": cb.get("name", ""),
                            }
                            yield LLMStreamEvent.tool_call(
                                ToolCallDelta(
                                    index=idx,
                                    id=cb.get("id"),
                                    name=cb.get("name"),
                                    arguments_delta="",
                                )
                            )
                        elif btype == "thinking":
                            thinking_acc[idx] = {"thinking": "", "signature": ""}

                    elif ev_type == "content_block_delta":
                        idx = ev.get("index", 0)
                        delta = ev.get("delta") or {}
                        delta_type = delta.get("type", "")

                        if delta_type == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                yield LLMStreamEvent.text(text)

                        elif delta_type == "thinking_delta":
                            thinking = delta.get("thinking", "")
                            if thinking:
                                yield LLMStreamEvent.reasoning(thinking)
                                if idx in thinking_acc:
                                    thinking_acc[idx]["thinking"] += thinking

                        elif delta_type == "signature_delta":
                            sig = delta.get("signature", "")
                            if sig and idx in thinking_acc:
                                thinking_acc[idx]["signature"] = sig

                        elif delta_type == "input_json_delta":
                            partial = delta.get("partial_json", "")
                            if partial:
                                yield LLMStreamEvent.tool_call(
                                    ToolCallDelta(
                                        index=idx,
                                        id=None,
                                        name=None,
                                        arguments_delta=partial,
                                    )
                                )

                    elif ev_type == "message_delta":
                        delta = ev.get("delta") or {}
                        stop_reason = delta.get("stop_reason")
                        msg_usage = ev.get("usage") or {}
                        usage_acc.update(msg_usage)

                        usage_obj = (
                            TokenUsage.from_anthropic(usage_acc)
                            if usage_acc
                            else None
                        )
                        yield LLMStreamEvent.done(
                            finish_reason=self._map_stop_reason(stop_reason),
                            usage=usage_obj,
                            response_id=response_id,
                            thinking_blocks=self._build_thinking_from_acc(thinking_acc),
                        )

        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    @staticmethod
    def _build_thinking_from_acc(
        thinking_acc: Dict[int, Dict[str, str]],
    ) -> List[dict]:
        """Build thinking block dicts from accumulated streaming data."""
        blocks = []
        for idx in sorted(thinking_acc):
            acc = thinking_acc[idx]
            if acc.get("signature"):
                blocks.append({
                    "type": "thinking",
                    "thinking": acc["thinking"],
                    "signature": acc["signature"],
                })
        return blocks

    # ── Core call ──────────────────────────────────────────────────────

    def _call(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, Iterator[LLMStreamEvent]]:
        """Run Claude LLM (sync).

        - non-streaming: returns LLMOutput
        - streaming: returns Iterator[LLMStreamEvent]
        """
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        client = self._new_client()
        system_prompt, anthropic_messages = au_messages_to_anthropic(messages)
        tools = kwargs.pop("tools", None)
        if tools:
            tools = _convert_openai_tools_to_anthropic(tools)
        tool_choice = kwargs.pop("tool_choice", None)
        if tool_choice is not None:
            tool_choice = _convert_openai_tool_choice_to_anthropic(tool_choice)

        # Build request kwargs
        ext_params = (self.ext_params or {}).copy()
        extra_body = kwargs.pop("extra_body", {}) or {}
        ext_params.update(extra_body)

        create_kwargs: Dict[str, Any] = {
            "messages": anthropic_messages,
            "model": kwargs.pop("model", self.model_name),
            "temperature": kwargs.pop("temperature", self.temperature),
            "max_tokens": kwargs.pop("max_tokens", self.max_tokens) or 4096,
            **ext_params,
            **kwargs,
        }
        if system_prompt:
            create_kwargs["system"] = system_prompt

        if tools:
            create_kwargs["tools"] = tools
        if tool_choice is not None:
            create_kwargs["tool_choice"] = tool_choice

        if not streaming:
            response = client.messages.create(**create_kwargs)
            return self._build_llm_output(response)

        # Streaming
        create_kwargs["stream"] = True
        raw_stream = client.messages.create(**create_kwargs)
        return self._iter_stream_events(raw_stream)

    async def _acall(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, AsyncIterator[LLMStreamEvent]]:
        """Run Claude LLM (async).

        - non-streaming: returns LLMOutput
        - streaming: returns AsyncIterator[LLMStreamEvent]
        """
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        async_client = self._new_async_client()
        system_prompt, anthropic_messages = au_messages_to_anthropic(messages)
        tools = kwargs.pop("tools", None)
        if tools:
            tools = _convert_openai_tools_to_anthropic(tools)
        tool_choice = kwargs.pop("tool_choice", None)
        if tool_choice is not None:
            tool_choice = _convert_openai_tool_choice_to_anthropic(tool_choice)

        ext_params = (self.ext_params or {}).copy()
        extra_body = kwargs.pop("extra_body", {}) or {}
        ext_params.update(extra_body)

        create_kwargs: Dict[str, Any] = {
            "messages": anthropic_messages,
            "model": kwargs.pop("model", self.model_name),
            "temperature": kwargs.pop("temperature", self.temperature),
            "max_tokens": kwargs.pop("max_tokens", self.max_tokens) or 4096,
            **ext_params,
            **kwargs,
        }
        if system_prompt:
            create_kwargs["system"] = system_prompt

        if tools:
            create_kwargs["tools"] = tools
        if tool_choice is not None:
            create_kwargs["tool_choice"] = tool_choice

        if not streaming:
            response = await async_client.messages.create(**create_kwargs)
            return self._build_llm_output(response)

        # Streaming
        create_kwargs["stream"] = True
        raw_stream = await async_client.messages.create(**create_kwargs)
        return self._aiter_stream_events(raw_stream)

    # ── Token / context utils ──────────────────────────────────────────

    def get_num_tokens(self, text: str) -> int:
        client = self._new_client()
        return client.count_tokens(text)

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return CLAUDE_MAX_CONTEXT_LENGTH.get(self.model_name, 200_000)

    # ── Component config ───────────────────────────────────────────────

    def set_by_agent_model(self, **kwargs) -> "ClaudeLLM":
        copied_obj = super().set_by_agent_model(**kwargs)
        if kwargs.get("api_key"):
            copied_obj.api_key = kwargs["api_key"]
        if kwargs.get("api_url"):
            copied_obj.api_url = kwargs["api_url"]
        if kwargs.get("proxy"):
            copied_obj.proxy = kwargs["proxy"]
        return copied_obj

    def initialize_by_component_configer(
        self, component_configer: LLMConfiger
    ) -> "ClaudeLLM":
        super().initialize_by_component_configer(component_configer)
        if 'api_key' in component_configer.configer.value:
            api_key = component_configer.configer.value.get('api_key')
            self.api_key = process_yaml_func(api_key, component_configer.yaml_func_instance)
        if 'api_url' in component_configer.configer.value:
            api_url = component_configer.configer.value.get('api_url')
            self.api_url = process_yaml_func(api_url, component_configer.yaml_func_instance)
        if 'proxy' in component_configer.configer.value:
            self.proxy = component_configer.configer.value.get('proxy')
        if 'connection_pool_limits' in component_configer.configer.value:
            self.connection_pool_limits = component_configer.configer.value.get('connection_pool_limits')
        if "extra_body" in component_configer.configer.value:
            self.ext_params = component_configer.configer.value["extra_body"]
        return self
