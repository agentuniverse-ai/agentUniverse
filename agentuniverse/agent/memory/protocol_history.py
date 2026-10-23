"""Opt-in literal chat history, including modern function-tool exchanges.

This bridge never executes tools or interpolates history as a prompt template.
The versioned metadata envelope survives existing SQL/JSON memory converters;
legacy Message.as_langchain() and all storage schemas remain unchanged.
"""

import json
from copy import deepcopy
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agentuniverse.agent.memory.message import Message

_KEY = "au_protocol_history"
_ROLE = {
    "human": "user",
    "ai": "assistant",
    "user": "user",
    "assistant": "assistant",
    "system": "system",
    "tool": "tool",
}
_TYPE = {"user": "human", "assistant": "ai", "system": "system", "tool": "tool"}
_FIELDS = {"role", "content", "tool_calls", "tool_call_id", "name"}


def _text_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _validate_message(value: dict) -> dict:
    """Validate our deliberately small OpenAI Chat Completions subset."""
    if not isinstance(value, dict) or set(value) - _FIELDS:
        raise ValueError("Unsupported history fields; expected a chat message object")
    role = value.get("role")
    if not isinstance(role, str) or role not in _TYPE:
        raise ValueError("History role must be system, user, assistant or tool")
    content = value.get("content")
    calls = value.get("tool_calls")
    if content is None:
        if role != "assistant" or not calls:
            raise ValueError("Only an assistant tool-call message may have null content")
    elif isinstance(content, list):
        # Images are user input only; reject unfamiliar block formats rather than
        # silently flattening them or claiming all provider modalities are supported.
        if role != "user" or not content:
            raise ValueError("Nonempty multimodal blocks are supported only for user messages")
        for block in content:
            if not isinstance(block, dict):
                raise ValueError("Content blocks must be objects")
            if block.get("type") == "text":
                if set(block) != {"type", "text"} or not isinstance(block["text"], str):
                    raise ValueError("Invalid text content block")
            elif block.get("type") == "image_url":
                image = block.get("image_url")
                if set(block) != {"type", "image_url"} or not isinstance(image, dict) or set(image) - {"url", "detail"}:
                    raise ValueError("Invalid image_url content block")
                _text_id(image.get("url"), "Image URL")
                if image.get("detail", "auto") not in {"auto", "low", "high"}:
                    raise ValueError("Invalid image detail")
            else:
                raise ValueError("Unsupported content block type")
    elif not isinstance(content, str):
        raise ValueError("History content must be text, user blocks or assistant tool-call null")
    if "name" in value:
        _text_id(value["name"], "Message name")
    if "tool_calls" in value:
        if role != "assistant" or not isinstance(calls, list) or not calls:
            raise ValueError("tool_calls requires a nonempty assistant call list")
        for call in calls:
            if not isinstance(call, dict) or set(call) != {"id", "type", "function"}:
                raise ValueError("Invalid function tool call")
            _text_id(call["id"], "Tool call ID")
            function = call["function"]
            if call["type"] != "function" or not isinstance(function, dict) or set(function) != {"name", "arguments"}:
                raise ValueError("Only function tool calls are supported")
            _text_id(function["name"], "Function name")
            if not isinstance(function["arguments"], str):
                raise ValueError("Function arguments must be a JSON object string")
            try:
                arguments = json.loads(function["arguments"])
                json.dumps(arguments, allow_nan=False)
            except (ValueError, TypeError, RecursionError) as error:
                raise ValueError("Function arguments must be finite JSON") from error
            if not isinstance(arguments, dict):
                raise ValueError("Function arguments must decode to an object")
    if role == "tool":
        _text_id(value.get("tool_call_id"), "Tool result call ID")
    elif "tool_call_id" in value:
        raise ValueError("Only a tool result may contain tool_call_id")
    return deepcopy(value)


class ProtocolHistory:
    """Stateless, opt-in conversion for stored literal history.

    Storage conversion accepts incomplete fragments; conversion for model input
    requires every tool call to have exactly one subsequent result. Bounds are
    rejection limits, not lossy truncation or context-window selection.
    """

    @staticmethod
    def _bounded(values: list, max_messages: int, max_bytes: int) -> None:
        if type(max_messages) is not int or max_messages < 1 or type(max_bytes) is not int or max_bytes < 1:
            raise ValueError("History limits must be positive integers")
        if not isinstance(values, list) or len(values) > max_messages:
            raise ValueError("History must be a list within max_messages")
        try:
            size = len(json.dumps(values, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        except (TypeError, ValueError, RecursionError) as error:
            raise ValueError("History must contain finite JSON values") from error
        if size > max_bytes:
            raise ValueError("History exceeds max_bytes; select complete turns explicitly")

    @classmethod
    def from_wire(
        cls,
        values: list[dict],
        *,
        message_ids: list[str | None] | None = None,
        max_messages: int = 256,
        max_bytes: int = 2_000_000,
    ) -> list[Message]:
        """Store a wire fragment without losing tool arguments or literal braces.

        Call/result pairing is checked when preparing the full model input, not
        while storing an assistant response before its tool results exist.
        """
        cls._bounded(values, max_messages, max_bytes)
        ids = message_ids if message_ids is not None else [None] * len(values)
        if not isinstance(ids, list) or len(ids) != len(values):
            raise ValueError("message_ids must align with the input messages")
        result = []
        for raw, message_id in zip(values, ids):
            value = _validate_message(raw)
            if message_id is not None:
                _text_id(message_id, "Message ID")
            envelope = {
                "version": 1,
                "message_id": message_id,
                **{key: value[key] for key in ("tool_calls", "tool_call_id", "name") if key in value},
            }
            result.append(
                Message(
                    id=message_id, type=_TYPE[value["role"]], content=value.get("content"), metadata={_KEY: envelope}
                )
            )
        return result

    @classmethod
    def to_wire(cls, messages: list[Message], *, max_messages: int = 256, max_bytes: int = 2_000_000) -> list[dict]:
        """Prepare a complete history for OpenAILLM.call/acall, rejecting orphan tools."""
        cls._bounded([], max_messages, max_bytes)
        if not isinstance(messages, list) or len(messages) > max_messages:
            raise ValueError("History must be a list within max_messages")
        result = []
        for message in messages:
            if not isinstance(message, Message):
                raise ValueError("Expected agentUniverse Message instances")
            role = _ROLE.get(message.type)
            if role is None:
                raise ValueError("Unsupported stored history role")
            value = {"role": role, "content": deepcopy(message.content)}
            envelope = (message.metadata or {}).get(_KEY)
            if envelope is not None:
                if (
                    not isinstance(envelope, dict)
                    or type(envelope.get("version")) is not int
                    or envelope["version"] != 1
                    or set(envelope) - {"version", "message_id", "tool_calls", "tool_call_id", "name"}
                ):
                    raise ValueError("Unsupported protocol history envelope")
                if envelope.get("message_id") is not None:
                    _text_id(envelope["message_id"], "Stored message ID")
                value.update(
                    {key: deepcopy(envelope[key]) for key in ("tool_calls", "tool_call_id", "name") if key in envelope}
                )
            result.append(_validate_message(value))
        cls._bounded(result, max_messages, max_bytes)
        cls._validate_pairs(result)
        return result

    @staticmethod
    def _validate_pairs(values: list[dict]) -> None:
        pending, seen = set(), set()
        for message in values:
            if message["role"] == "tool":
                call_id = message["tool_call_id"]
                if call_id not in pending:
                    raise ValueError("Orphan or duplicate tool result in history")
                pending.remove(call_id)
                continue
            if pending:
                raise ValueError("A non-tool message interrupts pending tool results")
            for call in message.get("tool_calls", []):
                call_id = call["id"]
                if call_id in seen:
                    raise ValueError("Duplicate tool call ID in history")
                seen.add(call_id)
                pending.add(call_id)
        if pending:
            raise ValueError("History ends with unresolved tool calls")

    @classmethod
    def as_langchain(cls, messages: list[Message], **limits):
        """Create literal BaseMessages, suitable for MessagesPlaceholder or invoke()."""
        values = cls.to_wire(messages, **limits)
        result = []
        for message, value in zip(messages, values):
            envelope = (message.metadata or {}).get(_KEY, {})
            message_id = envelope.get("message_id", message.id)
            common = {
                "content": value["content"] if value["content"] is not None else "",
                "id": str(message_id) if message_id is not None else None,
            }
            if "name" in value:
                common["name"] = value["name"]
            additional = {"name": value["name"]} if "name" in value else {}
            role = value["role"]
            if role == "assistant":
                if "tool_calls" in value:
                    additional["tool_calls"] = value["tool_calls"]
                result.append(AIMessage(**common, additional_kwargs=additional))
            elif role == "tool":
                result.append(ToolMessage(**common, tool_call_id=value["tool_call_id"], additional_kwargs=additional))
            else:
                factory = HumanMessage if role == "user" else SystemMessage
                result.append(factory(**common, additional_kwargs=additional))
        return result
