# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/6 16:24
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: transfer_utils.py

from typing import Any, List, Dict


# ---------------------------
# Openai helpers
# ---------------------------

def openai_enum_to_role(v: Any) -> str:
    s = v.value if hasattr(v, "value") else v
    s = str(s).lower() if s is not None else ""
    if s in ("system",):
        return "system"
    if s in ("human", "user"):
        return "user"
    if s in ("ai", "assistant"):
        return "assistant"
    if s in ("tool",):
        return "tool"
    # fallback
    return "user"


def openai_normalize_content(content: Any) -> Any:
    if content is None:
        return None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for x in content:
            if isinstance(x, str):
                out.append({"type": "text", "text": x})
            elif isinstance(x, dict):
                out.append(x)
            else:
                out.append({"type": "text", "text": str(x)})
        return out
    return str(content)


def au_messages_to_openai(messages: List[Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for m in messages or []:
        if isinstance(m, dict) and "role" in m:
            out.append(m)
            continue

        role = openai_enum_to_role(getattr(m, "type", None) or getattr(m, "role", None))
        item: Dict[str, Any] = {"role": role}

        content = openai_normalize_content(getattr(m, "content", None))
        if content is not None:
            item["content"] = content
        reasoning_content = getattr(m, "reasoning_content", None)
        if reasoning_content:
            item['reasoning_content'] = reasoning_content

        name = getattr(m, "name", None)
        if name:
            item["name"] = name

        tool_call_id = getattr(m, "tool_call_id", None)
        if tool_call_id:
            item["tool_call_id"] = tool_call_id

        # assistant 的 tool_calls（推荐字段）
        tool_calls = getattr(m, "tool_calls", None)
        if tool_calls:
            item["tool_calls"] = []
            for tc in tool_calls:
                # tc 可能是你定义的 ToolCall(BaseModel) 或 dict
                tc_d = tc.model_dump() if hasattr(tc, "model_dump") else (tc.dict() if hasattr(tc, "dict") else tc)
                fn = tc_d.get("function") or {}
                item["tool_calls"].append({
                    "id": tc_d.get("id"),
                    "type": tc_d.get("type", "function"),
                    "function": {
                        "name": fn.get("name"),
                        "arguments": fn.get("arguments") or "",
                    }
                })

        # deprecated function_call（兼容）
        function_call = getattr(m, "function_call", None)
        if function_call and not item.get("tool_calls"):
            fc = function_call.model_dump() if hasattr(function_call, "model_dump") else (
                function_call.dict() if hasattr(function_call, "dict") else function_call
            )
            item["function_call"] = {
                "name": fc.get("name"),
                "arguments": fc.get("arguments") or "",
            }

        out.append(item)
    return out
