#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time : 2025/10/28 19:30
# @Author : veteran
# @FileName : aws_bedrock_llm.py

from typing import Any, Optional, Union, Iterator, AsyncIterator, List, Dict

from pydantic import Field

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message, ToolCall
from agentuniverse.base.config.component_configer.configers.llm_configer import (
    LLMConfiger,
)
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import (
    LLMOutput,
    TokenUsage,
    LLMStreamEvent,
    StreamEventType,
    ToolCallDelta,
    FINISH_REASON_TYPE,
)

__all__ = ["AWSBedrockLLM"]

# ── 各模型最大上下文 ──────────────────────────────────────────
AWS_BEDROCK_MAX_CONTEXT_LENGTH: Dict[str, int] = {
    # Amazon Nova
    "amazon.nova-pro-v1:0": 300000,
    "amazon.nova-lite-v1:0": 300000,
    "amazon.nova-micro-v1:0": 128000,
    # Anthropic Claude
    "anthropic.claude-3-5-sonnet-20240620-v1:0": 200000,
    "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
    "anthropic.claude-3-haiku-20240307-v1:0": 200000,
    "anthropic.claude-3-opus-20240229-v1:0": 200000,
    "anthropic.claude-v2:1": 200000,
    "anthropic.claude-v2": 100000,
    "anthropic.claude-instant-v1": 100000,
    # Meta Llama
    "meta.llama3-70b-instruct-v1:0": 8192,
    "meta.llama3-8b-instruct-v1:0": 8192,
    # Mistral
    "mistral.mistral-7b-instruct-v0:2": 32000,
    "mistral.mixtral-8x7b-instruct-v0:1": 32000,
    "mistral.mistral-large-2402-v1:0": 32000,
    # Cohere
    "cohere.command-r-plus-v1:0": 128000,
    "cohere.command-r-v1:0": 128000,
    # Amazon Titan
    "amazon.titan-text-premier-v1:0": 32000,
    "amazon.titan-text-express-v1": 8000,
    "amazon.titan-text-lite-v1": 4000,
}

# Bedrock stopReason → 统一 finish_reason
_STOP_REASON_MAP: Dict[str, FINISH_REASON_TYPE] = {
    "end_turn": "stop",
    "stop_sequence": "stop",
    "max_tokens": "length",
    "tool_use": "tool_calls",
    "content_filtered": "content_filter",
    "guardrail_intervened": "content_filter",
}


def _map_stop_reason(reason: Optional[str]) -> Optional[FINISH_REASON_TYPE]:
    if not reason:
        return "stop"
    return _STOP_REASON_MAP.get(reason, "stop")


# ── Message 格式转换 ─────────────────────────────────────────

def _enum_to_role(v: Any) -> str:
    """ChatMessageEnum / str → Bedrock role (user | assistant)。"""
    s = v.value if hasattr(v, "value") else v
    s = str(s).lower() if s is not None else ""
    if s in ("system",):
        return "system"
    if s in ("human", "user"):
        return "user"
    if s in ("ai", "assistant"):
        return "assistant"
    if s in ("tool",):
        return "user"          # Bedrock 把 tool result 放在 user turn
    return "user"


def _build_bedrock_content(content: Any) -> List[Dict[str, Any]]:
    """把 content 统一转成 Bedrock content block 列表。"""
    if content is None:
        return []
    if isinstance(content, str):
        return [{"text": content}] if content else []
    if isinstance(content, list):
        blocks: List[Dict[str, Any]] = []
        for item in content:
            if isinstance(item, str):
                blocks.append({"text": item})
            elif isinstance(item, dict):
                # 已经是 Bedrock 格式 or OpenAI multimodal 格式
                if "text" in item and "type" not in item:
                    blocks.append(item)
                elif item.get("type") == "text":
                    blocks.append({"text": item.get("text", "")})
                elif item.get("type") == "image_url":
                    url = (item.get("image_url") or {}).get("url", "")
                    if url.startswith("data:"):
                        media_type, _, b64 = url.partition(";base64,")
                        media_type = media_type.replace("data:", "")
                        blocks.append({
                            "image": {
                                "format": media_type.split("/")[-1] or "png",
                                "source": {"bytes": b64},
                            }
                        })
                    else:
                        # URL 形式 Bedrock 不直接支持，降级为文本
                        blocks.append({"text": f"[image: {url}]"})
                else:
                    blocks.append(item)
            else:
                blocks.append({"text": str(item)})
        return blocks
    return [{"text": str(content)}]


def au_messages_to_bedrock(
    messages: List[Any],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """把 aU Message 列表转成 Bedrock Converse API 所需的 (system, messages)。

    Bedrock Converse API 要求：
      - system 独立传，格式 [{"text": "..."}]
      - messages 中只有 user / assistant，且必须交替出现
      - tool result 放在 user turn 的 toolResult content block 里
    """
    system_blocks: List[Dict[str, Any]] = []
    bedrock_msgs: List[Dict[str, Any]] = []

    for m in messages or []:
        # 兼容 raw dict
        if isinstance(m, dict) and "role" in m:
            role = m["role"]
            content = m.get("content")
            tool_calls_raw = m.get("tool_calls")
            tool_call_id = m.get("tool_call_id")
        else:
            role = _enum_to_role(
                getattr(m, "type", None) or getattr(m, "role", None)
            )
            content = getattr(m, "content", None)
            tool_calls_raw = getattr(m, "tool_calls", None)
            tool_call_id = getattr(m, "tool_call_id", None)

        # ── system → 提取到 system_blocks ──
        if role == "system":
            if isinstance(content, str):
                system_blocks.append({"text": content})
            elif isinstance(content, list):
                system_blocks.extend(_build_bedrock_content(content))
            continue

        # ── tool result（OpenAI role=tool）→ 合并进上一个 user turn ──
        if role == "tool" or tool_call_id:
            tool_result_block = {
                "toolResult": {
                    "toolUseId": tool_call_id or "",
                    "content": _build_bedrock_content(content),
                }
            }
            # 如果上一条是 user，合并进去；否则新建一条 user
            if bedrock_msgs and bedrock_msgs[-1]["role"] == "user":
                bedrock_msgs[-1]["content"].append(tool_result_block)
            else:
                bedrock_msgs.append({
                    "role": "user",
                    "content": [tool_result_block],
                })
            continue

        # ── assistant with tool_calls → toolUse content blocks ──
        if role == "assistant" and tool_calls_raw:
            blocks = _build_bedrock_content(content)
            for tc in tool_calls_raw:
                tc_d = (
                    tc.model_dump()
                    if hasattr(tc, "model_dump")
                    else (tc.dict() if hasattr(tc, "dict") else tc)
                )
                fn = tc_d.get("function") or {}
                import json as _json

                args_str = fn.get("arguments", "{}")
                try:
                    args = _json.loads(args_str) if isinstance(args_str, str) else args_str
                except _json.JSONDecodeError:
                    args = {"raw": args_str}

                blocks.append({
                    "toolUse": {
                        "toolUseId": tc_d.get("id", ""),
                        "name": fn.get("name", ""),
                        "input": args,
                    }
                })
            bedrock_msgs.append({"role": "assistant", "content": blocks})
            continue

        # ── 普通 user / assistant ──
        bedrock_role = "assistant" if role == "assistant" else "user"
        blocks = _build_bedrock_content(content)
        if not blocks:
            blocks = [{"text": ""}]

        # Bedrock 要求 user/assistant 交替；如果连续相同 role，合并
        if bedrock_msgs and bedrock_msgs[-1]["role"] == bedrock_role:
            bedrock_msgs[-1]["content"].extend(blocks)
        else:
            bedrock_msgs.append({"role": bedrock_role, "content": blocks})

    return system_blocks, bedrock_msgs


def _build_tool_config(tools: Optional[List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    """把 OpenAI-style tools 列表转成 Bedrock toolConfig。

    OpenAI 格式:
      {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}

    Bedrock 格式:
      {"tools": [{"toolSpec": {"name": ..., "description": ..., "inputSchema": {"json": ...}}}]}
    """
    if not tools:
        return None
    bedrock_tools = []
    for t in tools:
        fn = t.get("function") or t
        spec: Dict[str, Any] = {
            "name": fn.get("name", ""),
        }
        if fn.get("description"):
            spec["description"] = fn["description"]
        if fn.get("parameters"):
            spec["inputSchema"] = {"json": fn["parameters"]}
        bedrock_tools.append({"toolSpec": spec})
    return {"tools": bedrock_tools} if bedrock_tools else None


# ── TokenUsage 构建 ──────────────────────────────────────────

def _parse_bedrock_usage(usage: Optional[Dict[str, Any]]) -> TokenUsage:
    """从 Bedrock response 的 usage 字段构建 TokenUsage。"""
    if not usage:
        return TokenUsage()
    return TokenUsage(
        text_in=usage.get("inputTokens", 0),
        text_out=usage.get("outputTokens", 0),
        # Bedrock 目前没有细分 cached / image / audio，留 0 即可
    )


# ══════════════════════════════════════════════════════════════
# AWSBedrockLLM
# ══════════════════════════════════════════════════════════════

class AWSBedrockLLM(LLM):
    """AWS Bedrock LLM — 基于 boto3 Converse / ConverseStream API。

    输出协议与 OpenAIStyleLLM 一致：
      - 非流式: 返回 LLMOutput
      - 流式:   返回 Iterator[LLMStreamEvent] / AsyncIterator[LLMStreamEvent]

    Args:
        aws_access_key_id:     AWS Access Key（可选，走默认凭证链）
        aws_secret_access_key: AWS Secret Key
        aws_session_token:     临时凭证 Session Token
        aws_region:            区域，默认 us-east-1
    """

    aws_access_key_id: Optional[str] = Field(
        default_factory=lambda: get_from_env("AWS_ACCESS_KEY_ID")
    )
    aws_secret_access_key: Optional[str] = Field(
        default_factory=lambda: get_from_env("AWS_SECRET_ACCESS_KEY")
    )
    aws_session_token: Optional[str] = Field(
        default_factory=lambda: get_from_env("AWS_SESSION_TOKEN")
    )
    aws_region: Optional[str] = Field(
        default_factory=lambda: get_from_env("AWS_REGION") or "us-east-1"
    )

    # ── 内部客户端缓存 ──
    _boto_client: Any = None
    _async_client: Any = None

    class Config:
        arbitrary_types_allowed = True

    # ─────────────────────────────────────────────────────────
    # Client
    # ─────────────────────────────────────────────────────────

    def _get_boto_client(self):
        """懒初始化 boto3 bedrock-runtime 同步客户端。"""
        if self._boto_client is not None:
            return self._boto_client
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is required for AWS Bedrock LLM. "
                "Install it with: pip install boto3"
            )

        session_kwargs: Dict[str, Any] = {"region_name": self.aws_region}
        if self.aws_access_key_id:
            session_kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            session_kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            session_kwargs["aws_session_token"] = self.aws_session_token

        self._boto_client = boto3.client("bedrock-runtime", **session_kwargs)
        return self._boto_client

    def _get_async_boto_client(self):
        """懒初始化 aioboto3 bedrock-runtime 异步客户端 context manager。"""
        if self._async_client is not None:
            return self._async_client
        try:
            import aioboto3
        except ImportError:
            raise ImportError(
                "aioboto3 is required for async AWS Bedrock calls. "
                "Install it with: pip install aioboto3"
            )

        session_kwargs: Dict[str, Any] = {"region_name": self.aws_region}
        if self.aws_access_key_id:
            session_kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            session_kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            session_kwargs["aws_session_token"] = self.aws_session_token

        session = aioboto3.Session(**session_kwargs)
        # 返回 context manager；调用方需要 async with
        return session.client("bedrock-runtime")

    # ─────────────────────────────────────────────────────────
    # 请求参数构建
    # ─────────────────────────────────────────────────────────

    def _build_converse_params(
        self, messages: list, **kwargs: Any
    ) -> Dict[str, Any]:
        """构建 converse / converseStream 的公共参数。"""
        system_blocks, bedrock_messages = au_messages_to_bedrock(messages)

        params: Dict[str, Any] = {
            "modelId": kwargs.pop("model", self.model_name),
            "messages": bedrock_messages,
        }

        if system_blocks:
            params["system"] = system_blocks

        # inferenceConfig
        inference_config: Dict[str, Any] = {}
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        if max_tokens:
            inference_config["maxTokens"] = max_tokens
        temperature = kwargs.pop("temperature", self.temperature)
        if temperature is not None:
            inference_config["temperature"] = temperature
        top_p = kwargs.pop("top_p", None)
        if top_p is not None:
            inference_config["topP"] = top_p
        stop = kwargs.pop("stop", None) or kwargs.pop("stop_sequences", None)
        if stop:
            inference_config["stopSequences"] = (
                stop if isinstance(stop, list) else [stop]
            )
        if inference_config:
            params["inferenceConfig"] = inference_config

        # toolConfig（OpenAI-style tools → Bedrock toolConfig）
        tools = kwargs.pop("tools", None)
        tool_config = _build_tool_config(tools)
        if tool_config:
            params["toolConfig"] = tool_config

        return params

    # ─────────────────────────────────────────────────────────
    # 非流式响应解析
    # ─────────────────────────────────────────────────────────

    def _build_llm_output(self, response: Dict[str, Any]) -> LLMOutput:
        """从 Bedrock converse 响应构建 LLMOutput。"""
        output_msg = (response.get("output") or {}).get("message") or {}
        content_blocks = output_msg.get("content") or []

        text_parts: List[str] = []
        tool_calls: List[ToolCall] = []

        for block in content_blocks:
            if "text" in block:
                text_parts.append(block["text"])
            elif "toolUse" in block:
                tu = block["toolUse"]
                import json as _json

                args = tu.get("input", {})
                args_str = (
                    _json.dumps(args, ensure_ascii=False)
                    if isinstance(args, dict)
                    else str(args)
                )
                tool_calls.append(
                    ToolCall.create(
                        id=tu.get("toolUseId", ""),
                        name=tu.get("name", ""),
                        arguments=args_str,
                    )
                )

        text = "".join(text_parts)
        stop_reason = _map_stop_reason(response.get("stopReason"))
        usage = _parse_bedrock_usage(response.get("usage"))

        message = Message(
            type=ChatMessageEnum.ASSISTANT,
            content=text or None,
            tool_calls=tool_calls if tool_calls else None,
        )

        return LLMOutput(
            raw=response,
            text=text,
            message=message,
            finish_reason=stop_reason,
            usage=usage,
            response_id=response.get("ResponseMetadata", {})
            .get("RequestId"),
        )

    # ─────────────────────────────────────────────────────────
    # 流式响应解析
    # ─────────────────────────────────────────────────────────

    def _iter_stream_events(
            self, stream_response: Dict[str, Any]
    ) -> Iterator[LLMStreamEvent]:
        current_tool_index = -1
        request_id = stream_response.get("ResponseMetadata", {}).get(
            "RequestId"
        )

        stream = stream_response.get("stream")
        if stream is None:
            yield LLMStreamEvent.err("Bedrock response missing 'stream' key")
            return

        try:
            for event in stream:
                yield from self._parse_stream_event(
                    event, request_id, current_tool_index
                )
                if "contentBlockStart" in event:
                    start = event["contentBlockStart"]
                    if "toolUse" in start.get("start", {}):
                        current_tool_index = start.get(
                            "contentBlockIndex", current_tool_index + 1
                        )
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    async def _aiter_stream_events(
        self, stream_response: Dict[str, Any]
    ) -> AsyncIterator[LLMStreamEvent]:
        """异步：从 converseStream 的 EventStream 产出 LLMStreamEvent。"""
        current_tool_index = -1
        request_id = (
            stream_response.get("ResponseMetadata", {}).get("RequestId")
        )

        try:
            async for event in stream_response.get("stream", []):
                for evt in self._parse_stream_event(
                    event, request_id, current_tool_index
                ):
                    yield evt
                if "contentBlockStart" in event:
                    start = event["contentBlockStart"]
                    if "toolUse" in start.get("start", {}):
                        current_tool_index = start.get(
                            "contentBlockIndex", current_tool_index + 1
                        )
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    def _parse_stream_event(
        self,
        event: Dict[str, Any],
        request_id: Optional[str],
        current_tool_index: int,
    ) -> List[LLMStreamEvent]:
        """解析单个 Bedrock stream event 为 LLMStreamEvent 列表。

        Bedrock ConverseStream 事件类型：
          - messageStart: 消息开始，含 role
          - contentBlockStart: 内容块开始（text 或 toolUse）
          - contentBlockDelta: 内容增量
          - contentBlockStop: 内容块结束
          - messageStop: 消息结束，含 stopReason
          - metadata: 含 usage
        """
        events: List[LLMStreamEvent] = []

        # ── contentBlockStart: tool_use 开始 ──
        if "contentBlockStart" in event:
            start_block = event["contentBlockStart"]
            start = start_block.get("start", {})
            if "toolUse" in start:
                tu = start["toolUse"]
                idx = start_block.get("contentBlockIndex", current_tool_index + 1)
                events.append(
                    LLMStreamEvent.tool_call(
                        ToolCallDelta(
                            index=idx,
                            id=tu.get("toolUseId"),
                            name=tu.get("name"),
                            arguments_delta="",
                        )
                    )
                )

        # ── contentBlockDelta ──
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"].get("delta", {})
            if "text" in delta:
                events.append(LLMStreamEvent.text(delta["text"]))
            if "toolUse" in delta:
                # toolUse delta 只有 input（JSON 增量字符串）
                input_delta = delta["toolUse"].get("input", "")
                if input_delta:
                    idx = event["contentBlockDelta"].get(
                        "contentBlockIndex", max(current_tool_index, 0)
                    )
                    events.append(
                        LLMStreamEvent.tool_call(
                            ToolCallDelta(
                                index=idx,
                                arguments_delta=input_delta,
                            )
                        )
                    )
            # reasoning（部分 Bedrock 模型可能返回）
            if "reasoningContent" in delta:
                r = delta["reasoningContent"].get("text", "")
                if r:
                    events.append(LLMStreamEvent.reasoning(r))

        # ── messageStop ──
        if "messageStop" in event:
            stop_reason = _map_stop_reason(
                event["messageStop"].get("stopReason")
            )
            events.append(
                LLMStreamEvent.done(
                    finish_reason=stop_reason or "stop",
                    response_id=request_id,
                )
            )

        # ── metadata（含 usage，通常在 stream 末尾） ──
        if "metadata" in event:
            usage_raw = event["metadata"].get("usage")
            if usage_raw:
                events.append(
                    LLMStreamEvent(
                        type=StreamEventType.USAGE,
                        usage=_parse_bedrock_usage(usage_raw),
                    )
                )

        return events

    def _build_aioboto3_session_kwargs(self) -> Dict[str, Any]:
        """构建 aioboto3 session 参数。"""
        kwargs: Dict[str, Any] = {"region_name": self.aws_region}
        if self.aws_access_key_id:
            kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            kwargs["aws_session_token"] = self.aws_session_token
        return kwargs

    async def _aiter_stream_events_with_client(
            self, params: Dict[str, Any]
    ) -> AsyncIterator[LLMStreamEvent]:
        """异步流式：在 async generator 内部持有 aioboto3 client 生命周期。"""
        try:
            import aioboto3
        except ImportError:
            yield LLMStreamEvent.err(
                "aioboto3 is required. Install: pip install aioboto3"
            )
            return

        session_kwargs = self._build_aioboto3_session_kwargs()
        session = aioboto3.Session(**session_kwargs)

        async with session.client("bedrock-runtime") as client:
            try:
                response = await client.converse_stream(**params)
            except Exception as e:
                yield LLMStreamEvent.err(
                    f"Bedrock converse_stream failed: {e}"
                )
                return

            current_tool_index = -1
            request_id = response.get("ResponseMetadata", {}).get(
                "RequestId"
            )

            stream = response.get("stream")
            if stream is None:
                yield LLMStreamEvent.err(
                    "Bedrock response missing 'stream' key"
                )
                return

            try:
                # aioboto3 的 EventStream 是 async iterable，用 async for
                # 这里不再用 .get("stream", [])，已在上面做了 None 检查
                async for event in stream:
                    for evt in self._parse_stream_event(
                            event, request_id, current_tool_index
                    ):
                        yield evt
                    if "contentBlockStart" in event:
                        start = event["contentBlockStart"]
                        if "toolUse" in start.get("start", {}):
                            current_tool_index = start.get(
                                "contentBlockIndex",
                                current_tool_index + 1,
                            )
            except Exception as e:
                yield LLMStreamEvent.err(str(e))


    # ─────────────────────────────────────────────────────────
    # Core call（同步）
    # ─────────────────────────────────────────────────────────

    def _call(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, Iterator[LLMStreamEvent]]:
        """同步调用 Bedrock Converse API。

        - 非流式: 返回 LLMOutput
        - 流式:   返回 Iterator[LLMStreamEvent]
        """
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        params = self._build_converse_params(messages, **kwargs)
        client = self._get_boto_client()

        try:
            if streaming:
                response = client.converse_stream(**params)
                return self._iter_stream_events(response)
            else:
                response = client.converse(**params)
                return self._build_llm_output(response)
        except Exception as e:
            if streaming:
                def _err_gen():
                    yield LLMStreamEvent.err(f"Bedrock call failed: {e}")
                return _err_gen()
            raise RuntimeError(f"Bedrock call failed: {e}") from e

    # ─────────────────────────────────────────────────────────
    # Core call（异步）
    # ─────────────────────────────────────────────────────────

    async def _acall(
            self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, AsyncIterator[LLMStreamEvent]]:
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        params = self._build_converse_params(messages, **kwargs)

        if streaming:
            # 直接返回 async generator，其内部持有 client 生命周期
            return self._aiter_stream_events_with_client(params)

            # 非流式：正常 async with → 拿结果 → 关闭 client
        try:
            import aioboto3
        except ImportError:
            raise ImportError(
                "aioboto3 is required. Install: pip install aioboto3"
            )

        session_kwargs = self._build_aioboto3_session_kwargs()
        session = aioboto3.Session(**session_kwargs)

        try:
            async with session.client("bedrock-runtime") as client:
                response = await client.converse(**params)
                return self._build_llm_output(response)
        except Exception as e:
            raise RuntimeError(f"Bedrock async call failed: {e}") from e

    # ─────────────────────────────────────────────────────────
    # Component config
    # ─────────────────────────────────────────────────────────

    def initialize_by_component_configer(
        self, component_configer: LLMConfiger
    ) -> "LLM":
        """从 YAML 配置初始化。"""
        cfg = component_configer.configer.value

        if "aws_access_key_id" in cfg:
            self.aws_access_key_id = cfg["aws_access_key_id"]
        elif "aws_access_key_id_env" in cfg:
            self.aws_access_key_id = get_from_env(cfg["aws_access_key_id_env"])

        if "aws_secret_access_key" in cfg:
            self.aws_secret_access_key = cfg["aws_secret_access_key"]
        elif "aws_secret_access_key_env" in cfg:
            self.aws_secret_access_key = get_from_env(
                cfg["aws_secret_access_key_env"]
            )

        if "aws_session_token" in cfg:
            self.aws_session_token = cfg["aws_session_token"]

        if "aws_region" in cfg:
            self.aws_region = cfg["aws_region"]

        return super().initialize_by_component_configer(component_configer)

    def set_by_agent_model(self, **kwargs) -> "AWSBedrockLLM":
        """Agent 配置覆盖。"""
        copied_obj = super().set_by_agent_model(**kwargs)
        for key in (
            "aws_access_key_id",
            "aws_secret_access_key",
            "aws_session_token",
            "aws_region",
        ):
            if key in kwargs and kwargs[key]:
                setattr(copied_obj, key, kwargs[key])
        return copied_obj

    # ─────────────────────────────────────────────────────────
    # Token 相关
    # ─────────────────────────────────────────────────────────

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return AWS_BEDROCK_MAX_CONTEXT_LENGTH.get(self.model_name, 8_000)

    def get_num_tokens(self, text: str) -> int:
        """近似 token 计数。

        Bedrock 没有统一的 tokenizer 接口，
        对 Claude 系列用 tiktoken cl100k_base 近似，其余按 ~4 字符/token 估算。
        """
        if self.model_name and "anthropic" in self.model_name:
            try:
                import tiktoken

                enc = tiktoken.get_encoding("cl100k_base")
                return len(enc.encode(text))
            except ImportError:
                pass
        # fallback: ~4 chars per token
        return max(1, len(text) // 4)
