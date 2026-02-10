# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: wenxin_llm.py

from typing import Any, Union, AsyncIterator, Iterator, Optional, List, Dict

import qianfan
from pydantic import Field
from qianfan import QfResponse
from qianfan.resources.tools import tokenizer

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message, ToolCall, FunctionCall
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import (
    LLMOutput,
    TokenUsage,
    LLMStreamEvent,
    StreamEventType,
    ToolCallDelta,
)

TokenModelList = [
    'ernie-4.5-turbo-32k',
    'ernie-4.5-8k-preview',
    'ernie-4.0-8k',
    'ernie-3.5-8k',
    'ernie-speed-8k',
    'ernie-speed-128k',
    'ernie-lite-8k',
    'ernie-tiny-8k',
    'ernie-char-8k',
]


class WenXinLLM(LLM):
    """百度千帆（文心一言）LLM 封装。

    基于 qianfan SDK 的 ChatCompletion API。
    - 非流式：返回 LLMOutput
    - 流式：yield LLMStreamEvent，可通过 StreamReducer 聚合

    Attributes:
        api_key: 千帆 API 的 Access Key，默认读取 QIANFAN_AK 环境变量。
        secret_key: 千帆 API 的 Secret Key，默认读取 QIANFAN_SK 环境变量。
    """

    api_key: str = Field(default_factory=lambda: get_from_env("QIANFAN_AK"))
    secret_key: str = Field(default_factory=lambda: get_from_env("QIANFAN_SK"))

    # ---------------------------
    # Client
    # ---------------------------
    def _new_client(self) -> qianfan.ChatCompletion:
        if self.client is None:
            self.client = qianfan.ChatCompletion(ak=self.api_key, sk=self.secret_key)
        return self.client

    # ---------------------------
    # Response parsing helpers
    # ---------------------------
    @staticmethod
    def _parse_usage(body: Dict[str, Any]) -> Optional[TokenUsage]:
        """从千帆响应 body 中解析 token 用量。"""
        usage = body.get("usage")
        if not usage:
            return None
        return TokenUsage(
            text_in=usage.get("prompt_tokens", 0),
            text_out=usage.get("completion_tokens", 0),
        )

    @staticmethod
    def _parse_function_call(body: Dict[str, Any]) -> Optional[FunctionCall]:
        """解析千帆的 function_call 字段。"""
        fc = body.get("function_call")
        if not fc:
            return None
        import json
        arguments = fc.get("arguments", "")
        if isinstance(arguments, dict):
            arguments = json.dumps(arguments, ensure_ascii=False)
        return FunctionCall(
            name=fc.get("name", ""),
            arguments=arguments,
        )

    def _build_llm_output(self, response: QfResponse) -> Optional[LLMOutput]:
        """非流式：将 QfResponse 解析为 LLMOutput。"""
        body = response.body or {}
        text = body.get("result", "")

        # 解析 function_call
        function_call = self._parse_function_call(body)
        tool_calls: Optional[List[ToolCall]] = None
        if function_call:
            tool_calls = [
                ToolCall.create(
                    id=body.get("id", "call_0"),
                    name=function_call.name,
                    arguments=function_call.arguments,
                )
            ]

        # 构建 Message
        message = Message(
            type=ChatMessageEnum.ASSISTANT,
            content=text or None,
            tool_calls=tool_calls,
            function_call=function_call,
        )

        # 判断 finish_reason
        finish_reason = "stop"
        if function_call:
            finish_reason = "tool_calls"
        elif body.get("is_end") is False:
            finish_reason = None  # 未结束（一般非流式不会出现）

        return LLMOutput(
            raw=body,
            text=text,
            message=message,
            response_id=body.get("id"),
            finish_reason=finish_reason,
            usage=self._parse_usage(body),
        )

    def _iter_stream_events_from_chunk(self, body: Dict[str, Any]) -> Iterator[LLMStreamEvent]:
        """流式：将一个 chunk body 解析为 0..n 个 LLMStreamEvent。"""
        response_id = body.get("id")

        # text delta
        text = body.get("result")
        if text:
            yield LLMStreamEvent.text(text)

        # function_call（千帆在流式中也可能返回 function_call）
        fc = body.get("function_call")
        if fc:
            import json
            arguments = fc.get("arguments", "")
            if isinstance(arguments, dict):
                arguments = json.dumps(arguments, ensure_ascii=False)
            yield LLMStreamEvent.tool_call(
                ToolCallDelta(
                    index=0,
                    id=response_id,
                    name=fc.get("name"),
                    arguments_delta=arguments,
                )
            )

        # is_end -> done
        if body.get("is_end", False):
            finish_reason = "tool_calls" if fc else "stop"
            usage = self._parse_usage(body)
            yield LLMStreamEvent.done(
                finish_reason=finish_reason,
                usage=usage,
                response_id=response_id,
            )
        else:
            # 非终态但带 usage 的 chunk（某些模型每个 chunk 都带 usage）
            usage = self._parse_usage(body)
            if usage:
                yield LLMStreamEvent(type=StreamEventType.USAGE, usage=usage)

    # ---------------------------
    # Core call
    # ---------------------------
    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMStreamEvent]]:
        """同步调用千帆 API。

        - 非流式：返回 LLMOutput
        - 流式：返回 Iterator[LLMStreamEvent]
        """
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        client = self._new_client()
        chat_completion = client.do(
            messages=messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=streaming,
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            **kwargs,
        )

        if not streaming:
            return self._build_llm_output(chat_completion)
        return self._generate_stream_events(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMStreamEvent]]:
        """异步调用千帆 API。

        - 非流式：返回 LLMOutput
        - 流式：返回 AsyncIterator[LLMStreamEvent]
        """
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        client = self._new_client()
        chat_completion = await client.ado(
            messages=messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=streaming,
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            **kwargs,
        )

        if not streaming:
            return self._build_llm_output(chat_completion)
        return self._agenerate_stream_events(chat_completion)

    # ---------------------------
    # Streaming generators
    # ---------------------------
    def _generate_stream_events(self, stream) -> Iterator[LLMStreamEvent]:
        """同步流式：yield LLMStreamEvent。"""
        try:
            for chunk in stream:
                body = chunk.body if hasattr(chunk, "body") else {}
                yield from self._iter_stream_events_from_chunk(body)
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    async def _agenerate_stream_events(self, stream: AsyncIterator) -> AsyncIterator[LLMStreamEvent]:
        """异步流式：yield LLMStreamEvent。"""
        try:
            async for chunk in stream:
                body = chunk.body if hasattr(chunk, "body") else {}
                for evt in self._iter_stream_events_from_chunk(body):
                    yield evt
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    # ---------------------------
    # Token utils
    # ---------------------------
    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        res = self._new_client().get_model_info(self.model_name)
        if res.max_input_tokens:
            return res.max_input_tokens
        return res.max_input_chars

    def get_num_tokens(self, text: str) -> int:
        model_name = ""
        if self.model_name.lower() in TokenModelList:
            model_name = self.model_name.lower()
        token_cnt = tokenizer.Tokenizer().count_tokens(
            text=text,
            mode="remote",
            model=model_name,
        )
        return token_cnt

    # ---------------------------
    # Component config
    # ---------------------------
    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> "WenXinLLM":
        super().initialize_by_component_configer(component_configer)
        if "api_key" in component_configer.configer.value:
            api_key = component_configer.configer.value.get("api_key")
            self.api_key = process_yaml_func(api_key, component_configer.yaml_func_instance)
        if "secret_key" in component_configer.configer.value:
            secret_key = component_configer.configer.value.get("secret_key")
            self.secret_key = process_yaml_func(secret_key, component_configer.yaml_func_instance)
        return self