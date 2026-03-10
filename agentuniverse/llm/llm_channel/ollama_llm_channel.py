# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/7 19:26
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: ollama_llm_channel.py
import json
from typing import Any, Optional, Union, Iterator, AsyncIterator, List, Dict

from ollama import Options

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message, ToolCall
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_output import (
    LLMOutput,
    TokenUsage,
    LLMStreamEvent,
    ToolCallDelta,
)


def _au_messages_to_ollama(messages: List[Any]) -> List[Dict[str, Any]]:
    """将 AU Message 列表转为 Ollama chat 所需的 message 列表。

    Ollama 的 message 格式与 OpenAI 基本一致:
      {"role": "user"|"assistant"|"system"|"tool", "content": "...", ...}
    tool_calls 中的 arguments 是 dict（不是 JSON 字符串）。
    """
    out: List[Dict[str, Any]] = []
    for m in messages or []:
        # 已经是 dict 且带 role → 直接透传
        if isinstance(m, dict) and "role" in m:
            out.append(m)
            continue

        role_raw = getattr(m, "type", None) or getattr(m, "role", None)
        role = _enum_to_role(role_raw)
        item: Dict[str, Any] = {"role": role}

        content = getattr(m, "content", None)
        if content is not None:
            item["content"] = content if isinstance(content, str) else str(content)

        # tool 消息必须带 content（即使为空字符串）
        if role == "tool" and "content" not in item:
            item["content"] = ""

        # assistant 的 tool_calls
        tool_calls = getattr(m, "tool_calls", None)
        if tool_calls:
            item["tool_calls"] = []
            for tc in tool_calls:
                tc_d = tc.model_dump() if hasattr(tc, "model_dump") else (
                    tc.dict() if hasattr(tc, "dict") else tc
                )
                fn = tc_d.get("function") or {}
                args = fn.get("arguments", "")
                # Ollama 需要 dict 而非 JSON 字符串
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                item["tool_calls"].append({
                    "function": {
                        "name": fn.get("name", ""),
                        "arguments": args,
                    }
                })

        out.append(item)
    return out


def _enum_to_role(v: Any) -> str:
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
    return "user"


class OllamaLLMChannel(LLMChannel):
    """Ollama LLM Channel — 用于切换同一模型的不同 Ollama 服务实例。

    Non-streaming → LLMOutput
    Streaming     → Iterator[LLMStreamEvent] / AsyncIterator[LLMStreamEvent]
    """

    channel_api_base: Optional[str] = "http://localhost:11434"

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'OllamaLLMChannel':
        super()._initialize_by_component_configer(component_configer)
        return self

    # ------------------------------------------------------------------
    # Client builders
    # ------------------------------------------------------------------
    def _new_client(self):
        if self.client:
            return self.client
        from ollama import Client
        return Client(host=self.channel_api_base)

    def _new_async_client(self):
        if self.async_client:
            return self.async_client
        from ollama import AsyncClient
        return AsyncClient(host=self.channel_api_base)

    def _build_options(self, **overrides) -> Options:
        opts: Dict[str, Any] = {}
        ctx = self.max_context_length()
        if ctx:
            opts["num_ctx"] = ctx
        if self.max_tokens is not None:
            opts["num_predict"] = self.max_tokens
        if self.temperature is not None:
            opts["temperature"] = self.temperature
        if self.request_timeout is not None:
            opts["timeout"] = self.request_timeout
        if self.ext_info:
            opts.update(self.ext_info)
        opts.update(overrides)
        return Options(**opts)

    # ------------------------------------------------------------------
    # Response → LLMOutput / LLMStreamEvent helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_usage(raw: Dict[str, Any]) -> TokenUsage:
        """从 Ollama 响应中提取 token 用量。

        Ollama 返回的字段（非流式 & 流式最后一个 chunk）:
          prompt_eval_count  —  输入 token 数
          eval_count         —  输出 token 数
        """
        return TokenUsage(
            text_in=raw.get("prompt_eval_count", 0),
            text_out=raw.get("eval_count", 0),
        )

    @staticmethod
    def _parse_tool_calls(msg: Dict[str, Any]) -> Optional[List[ToolCall]]:
        """解析 Ollama 消息中的 tool_calls。

        Ollama tool_calls 格式:
          [{"function": {"name": "...", "arguments": {dict}}}]
        注意: Ollama 的 tool_call 没有 id 字段，我们自行生成。
        """
        raw_tcs = msg.get("tool_calls")
        if not raw_tcs:
            return None
        tool_calls: List[ToolCall] = []
        for i, tc in enumerate(raw_tcs):
            fn = tc.get("function") or {}
            args = fn.get("arguments", {})
            if isinstance(args, dict):
                args = json.dumps(args, ensure_ascii=False)
            tool_calls.append(
                ToolCall.create(
                    id=f"call_{i}",
                    name=fn.get("name", ""),
                    arguments=args,
                )
            )
        return tool_calls or None

    def _build_llm_output(self, raw: Dict[str, Any]) -> LLMOutput:
        """从 Ollama 非流式响应构建 LLMOutput。"""
        msg = raw.get("message") or {}
        content = msg.get("content", "")
        tool_calls = self._parse_tool_calls(msg)

        finish_reason = "tool_calls" if tool_calls else "stop"

        message = Message(
            type=ChatMessageEnum.ASSISTANT,
            content=content or None,
            tool_calls=tool_calls,
        )

        return LLMOutput(
            raw=raw,
            text=content,
            message=message,
            usage=self._parse_usage(raw),
            finish_reason=finish_reason,
        )

    # ------------------------------------------------------------------
    # Core calls
    # ------------------------------------------------------------------
    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMStreamEvent]]:
        streaming = kwargs.pop("stream", kwargs.pop("streaming", self.streaming))
        client = self._new_client()

        stop = kwargs.pop("stop", None)
        options = self._build_options()
        if stop:
            options.setdefault("stop", stop)

        # tools 透传（Ollama >= 0.4 支持 function calling）
        tools = kwargs.pop("tools", None)

        call_kwargs: Dict[str, Any] = dict(
            model=kwargs.pop("model", self.channel_model_name),
            messages=_au_messages_to_ollama(messages),
            options=options,
            stream=streaming,
        )
        if tools:
            call_kwargs["tools"] = tools

        res = client.chat(**call_kwargs)

        if not streaming:
            return self._build_llm_output(res)

        return self._generate_stream_events(res)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMStreamEvent]]:
        streaming = kwargs.pop("stream", kwargs.pop("streaming", self.streaming))
        client = self._new_async_client()

        stop = kwargs.pop("stop", None)
        options = self._build_options()
        if stop:
            options.setdefault("stop", stop)

        tools = kwargs.pop("tools", None)

        call_kwargs: Dict[str, Any] = dict(
            model=kwargs.pop("model", self.channel_model_name),
            messages=_au_messages_to_ollama(messages),
            options=options,
            stream=streaming,
        )
        if tools:
            call_kwargs["tools"] = tools

        res = await client.chat(**call_kwargs)

        if not streaming:
            return self._build_llm_output(res)

        return self._agenerate_stream_events(res)

    # ------------------------------------------------------------------
    # Streaming generators
    # ------------------------------------------------------------------
    def _generate_stream_events(self, stream) -> Iterator[LLMStreamEvent]:
        """同步流式：yield LLMStreamEvent。

        Ollama 流式 chunk 格式:
          {"message": {"role": "assistant", "content": "delta"}, "done": false}
          最后一个 chunk: {"message": {...}, "done": true, "eval_count": ..., ...}
        """
        try:
            for chunk in stream:
                raw = chunk if isinstance(chunk, dict) else dict(chunk)
                msg = raw.get("message") or {}

                # text delta
                content = msg.get("content")
                if content:
                    yield LLMStreamEvent.text(content)

                # tool_calls（Ollama 流式中极少出现，但保持兼容）
                tool_calls = msg.get("tool_calls")
                if tool_calls:
                    for i, tc in enumerate(tool_calls):
                        fn = tc.get("function") or {}
                        args = fn.get("arguments", {})
                        if isinstance(args, dict):
                            args = json.dumps(args, ensure_ascii=False)
                        yield LLMStreamEvent.tool_call(
                            ToolCallDelta(
                                index=i,
                                id=f"call_{i}",
                                name=fn.get("name"),
                                arguments_delta=args,
                            )
                        )

                # done
                if raw.get("done"):
                    has_tool_calls = bool(tool_calls)
                    yield LLMStreamEvent.done(
                        finish_reason="tool_calls" if has_tool_calls else "stop",
                        usage=self._parse_usage(raw),
                    )
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    async def _agenerate_stream_events(self, stream) -> AsyncIterator[LLMStreamEvent]:
        """异步流式：yield LLMStreamEvent。"""
        try:
            async for chunk in stream:
                raw = chunk if isinstance(chunk, dict) else dict(chunk)
                msg = raw.get("message") or {}

                content = msg.get("content")
                if content:
                    yield LLMStreamEvent.text(content)

                tool_calls = msg.get("tool_calls")
                if tool_calls:
                    for i, tc in enumerate(tool_calls):
                        fn = tc.get("function") or {}
                        args = fn.get("arguments", {})
                        if isinstance(args, dict):
                            args = json.dumps(args, ensure_ascii=False)
                        yield LLMStreamEvent.tool_call(
                            ToolCallDelta(
                                index=i,
                                id=f"call_{i}",
                                name=fn.get("name"),
                                arguments_delta=args,
                            )
                        )

                if raw.get("done"):
                    has_tool_calls = bool(tool_calls)
                    yield LLMStreamEvent.done(
                        finish_reason="tool_calls" if has_tool_calls else "stop",
                        usage=self._parse_usage(raw),
                    )
        except Exception as e:
            yield LLMStreamEvent.err(str(e))