# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: openai_style_llm.py

from typing import Any, Optional, AsyncIterator, Iterator, Union, List

import httpx
import openai
import tiktoken
from openai import OpenAI, AsyncOpenAI

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message, ToolCall, FunctionCall
from agentuniverse.base.config.component_configer.configers.llm_configer import (
    LLMConfiger,
)
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

__all__ = ['OpenAIStyleLLM']

from agentuniverse.llm.transfer_utils import au_messages_to_openai


class OpenAIStyleLLM(LLM):
    """OpenAI-style ChatCompletions wrapper.

    - Non-streaming: returns LLMOutput (with Message/ToolCalls/Usage/etc.)
    - Streaming: yields LLMStreamEvent (text/tool_call/usage/done/error)
      so you can aggregate via StreamReducer.
    """

    api_key: Optional[str] = None
    organization: Optional[str] = None
    api_base: Optional[str] = None
    proxy: Optional[str] = None
    client_args: Optional[dict] = None
    ext_params: Optional[dict] = {}
    ext_headers: Optional[dict] = {}

    # ---------------------------
    # Client builders
    # ---------------------------
    def _new_client(self) -> OpenAI:
        """Initialize the openai client."""
        if self.client is not None:
            return self.client
        return OpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def _new_async_client(self) -> AsyncOpenAI:
        """Initialize the openai async client."""
        if self.async_client is not None:
            return self.async_client
        return AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def _get_client(self, api_base: Optional[str]) -> OpenAI:
        api_base = api_base or self.api_base
        if not api_base:
            return self._new_client()
        c = self._client_pool.get(api_base)
        if c is None:
            c = OpenAI(
                api_key=self.api_key,
                organization=self.organization,
                base_url=api_base,
                timeout=self.request_timeout,
                max_retries=self.max_retries,
                http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,
                **(self.client_args or {}),
            )
            self._client_pool[api_base] = c
        return c

    def _get_async_client(self, api_base: Optional[str]) -> AsyncOpenAI:
        api_base = api_base or self.api_base
        if not api_base:
            return self._new_async_client()

        c = self._async_client_pool.get(api_base)
        if c is None:
            c = AsyncOpenAI(
                api_key=self.api_key,
                organization=self.organization,
                base_url=api_base,
                timeout=self.request_timeout,
                max_retries=self.max_retries,
                http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
                **(self.client_args or {}),
            )
            self._async_client_pool[api_base] = c
        return c

    def _new_client_with_api_base(self, api_base: Optional[str] = None) -> OpenAI:
        if self.client is not None:
            return self.client
        return OpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=api_base if api_base else self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def _new_async_client_with_api_base(
        self, api_base: Optional[str] = None
    ) -> AsyncOpenAI:
        if self.async_client is not None:
            return self.async_client
        return AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=api_base if api_base else self.api_base,
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    # ---------------------------
    # Small helpers
    # ---------------------------
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

    def _build_message_from_openai_message(self, msg: dict) -> Message:
        """把 OpenAI 的 message dict 变成你定义的 Message。"""
        tool_calls: Optional[List[ToolCall]] = None
        function_call: Optional[FunctionCall] = None

        # tool_calls（推荐字段）
        if msg.get("tool_calls"):
            tool_calls = []
            for i, tc in enumerate(msg.get("tool_calls") or []):
                tc = tc or {}
                if tc.get("type", "function") != "function":
                    # 你当前 ToolCall 只对标 function；其它类型先跳过/后续扩展
                    continue
                fn = (tc.get("function") or {}) if isinstance(tc.get("function"), dict) else {}
                tool_calls.append(
                    ToolCall.create(
                        id=tc.get("id") or f"call_{i}",
                        name=fn.get("name", ""),
                        arguments=fn.get("arguments", ""),
                    )
                )

        # function_call（deprecated 字段，兼容老实现/某些 openai-style 服务）
        if not tool_calls and msg.get("function_call"):
            fc = msg.get("function_call") or {}
            function_call = FunctionCall(
                name=fc.get("name", ""),
                arguments=fc.get("arguments", "") or "",
            )

        return Message(
            type=ChatMessageEnum.ASSISTANT,
            content=msg.get("content"),
            reasoning_content=msg.get("reasoning") or msg.get("reasoning_content"),
            refusal=msg.get("refusal"),
            tool_calls=tool_calls,
            function_call=function_call,
            name=msg.get("name"),
        )

    def _build_llm_output_from_chat_completion(self, chat_completion: Any) -> LLMOutput:
        """非流式：构造最终 LLMOutput（带 message/tool_calls/usage/finish_reason/response_id）。"""
        raw = self._to_dict(chat_completion)

        choices = raw.get("choices") or []
        choice0 = choices[0] if choices else {}

        msg = choice0.get("message") or {}
        content = msg.get("content")
        text = content if isinstance(content, str) else ""

        message = self._build_message_from_openai_message(msg)

        usage = TokenUsage.from_openai(raw.get("usage"))

        # 兼容某些 openai-style 服务附带 reasoning 字段（非官方 chat.completions 标准字段）
        reasoning_text = msg.get("reasoning") or msg.get("reasoning_content")

        return LLMOutput(
            raw=raw,
            text=text,
            message=message,
            response_id=raw.get("id"),
            finish_reason=choice0.get("finish_reason"),
            usage=usage,
            reasoning_text=reasoning_text,
        )

    def _iter_stream_events_from_chunk(self, chunk: dict) -> Iterator[LLMStreamEvent]:
        """流式：把一个 chunk 解析成 0..n 个 LLMStreamEvent。"""
        response_id = chunk.get("id")

        # usage（可能只在最后一个 chunk 出现；也可能 choices=[] 但带 usage）
        if chunk.get("usage"):
            yield LLMStreamEvent(type=StreamEventType.USAGE, usage=TokenUsage.from_openai(chunk.get("usage")))

        choices = chunk.get("choices") or []
        for choice in choices:
            choice = choice or {}
            delta = choice.get("delta") or {}

            # text delta
            if "content" in delta:
                c = delta.get("content")
                if c:
                    yield LLMStreamEvent.text(c)

            # reasoning delta（兼容字段：reasoning / reasoning_content）
            r = delta.get("reasoning") or delta.get("reasoning_content")
            if r:
                yield LLMStreamEvent.reasoning(r)

            # tool_calls delta（推荐字段）
            if delta.get("tool_calls"):
                for tc in delta.get("tool_calls") or []:
                    tc = tc or {}
                    fn = tc.get("function") or {}
                    yield LLMStreamEvent.tool_call(
                        ToolCallDelta(
                            index=tc.get("index", 0),
                            id=tc.get("id"),
                            name=fn.get("name"),
                            arguments_delta=fn.get("arguments") or "",
                        )
                    )

            # function_call delta（deprecated 字段）
            if delta.get("function_call"):
                fc = delta.get("function_call") or {}
                yield LLMStreamEvent.tool_call(
                    ToolCallDelta(
                        index=0,
                        id=None,
                        name=fc.get("name"),
                        arguments_delta=fc.get("arguments") or "",
                    )
                )

            # done
            finish_reason = choice.get("finish_reason")
            if finish_reason:
                usage_obj = TokenUsage.from_openai(chunk.get("usage")) if chunk.get("usage") else None
                yield LLMStreamEvent.done(
                    finish_reason=finish_reason,
                    usage=usage_obj,
                    response_id=response_id,
                )

    # ---------------------------
    # Core call
    # ---------------------------
    def _call(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, Iterator[LLMStreamEvent]]:
        """Run the OpenAI LLM (sync).

        - non-streaming: returns LLMOutput
        - streaming: returns iterator of LLMStreamEvent
        """
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        # ext_params merge
        ext_params = (self.ext_params or {}).copy()
        extra_body = kwargs.pop("extra_body", {}) or {}
        ext_params = {**ext_params, **extra_body}

        # ensure usage in streaming
        if streaming and "stream_options" not in ext_params:
            ext_params["stream_options"] = {"include_usage": True}

        # api_base override
        api_base = kwargs.pop("api_base", None)
        client = self._get_client(api_base)

        openai_messages = au_messages_to_openai(messages)
        chat_completion = client.chat.completions.create(
            messages=openai_messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=streaming,
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            extra_headers=kwargs.pop("extra_headers", self.ext_headers),
            extra_body=ext_params,
            **kwargs,
        )

        if not streaming:
            return self._build_llm_output_from_chat_completion(chat_completion)

        return self.generate_stream_events(chat_completion)

    async def _acall(
        self, messages: list, **kwargs: Any
    ) -> Union[LLMOutput, AsyncIterator[LLMStreamEvent]]:
        """Run the OpenAI LLM (async).

        - non-streaming: returns LLMOutput

        - streaming: returns async iterator of LLMStreamEvent
        """
        streaming = kwargs.pop("streaming", self.streaming)
        if "stream" in kwargs:
            streaming = kwargs.pop("stream")

        # ext_params merge
        ext_params = (self.ext_params or {}).copy()
        extra_body = kwargs.pop("extra_body", {}) or {}
        ext_params = {**ext_params, **extra_body}

        # ensure usage in streaming
        if streaming and "stream_options" not in ext_params:
            ext_params["stream_options"] = {"include_usage": True}

        # api_base override
        api_base = kwargs.pop("api_base", None)
        async_client = self._get_async_client(api_base)

        openai_messages = au_messages_to_openai(messages)
        chat_completion = await async_client.chat.completions.create(
            messages=openai_messages,
            model=kwargs.pop("model", self.model_name),
            temperature=kwargs.pop("temperature", self.temperature),
            stream=streaming,
            max_tokens=kwargs.pop("max_tokens", self.max_tokens),
            extra_headers=kwargs.pop("extra_headers", self.ext_headers),
            extra_body=ext_params,
            **kwargs,
        )

        if not streaming:
            return self._build_llm_output_from_chat_completion(chat_completion)

        return self.agenerate_stream_events(chat_completion)

    # ---------------------------
    # Streaming generators
    # ---------------------------
    def generate_stream_events(self, stream: openai.Stream) -> Iterator[LLMStreamEvent]:
        """Streaming: yield structured events."""
        try:
            for chunk in stream:
                d = self._to_dict(chunk)
                yield from self._iter_stream_events_from_chunk(d)
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    async def agenerate_stream_events(
        self, stream: AsyncIterator
    ) -> AsyncIterator[LLMStreamEvent]:
        """Async streaming: yield structured events."""
        try:
            async for chunk in stream:
                d = self._to_dict(chunk)
                for evt in self._iter_stream_events_from_chunk(d):
                    yield evt
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    def set_by_agent_model(self, **kwargs) -> "OpenAIStyleLLM":
        """Assign values of parameters to the OpenAILLM model in the agent configuration."""
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'api_key' in kwargs and kwargs['api_key']:
            copied_obj.api_key = kwargs['api_key']
        if 'api_base' in kwargs and kwargs['api_base']:
            copied_obj.api_base = kwargs['api_base']
        if 'proxy' in kwargs and kwargs['proxy']:
            copied_obj.proxy = kwargs['proxy']
        if 'client_args' in kwargs and kwargs['client_args']:
            copied_obj.client_args = kwargs['client_args']
        return copied_obj

    # ---------------------------
    # component config
    # ---------------------------
    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> "LLM":
        if 'api_base' in component_configer.configer.value:
            api_base = component_configer.configer.value.get('api_base')
            self.api_base = process_yaml_func(api_base, component_configer.yaml_func_instance)
        elif 'api_base_env' in component_configer.configer.value:
            self.api_base = get_from_env(component_configer.configer.value.get('api_base_env'))
        if 'api_key' in component_configer.configer.value:
            api_key = component_configer.configer.value.get('api_key')
            self.api_key = process_yaml_func(api_key, component_configer.yaml_func_instance)
        elif 'api_key_env' in component_configer.configer.value:
            self.api_key = get_from_env(component_configer.configer.value.get('api_key_env'))
        if 'organization' in component_configer.configer.value:
            organization = component_configer.configer.value.get('organization')
            self.organization = process_yaml_func(organization, component_configer.yaml_func_instance)
        if 'proxy' in component_configer.configer.value:
            proxy = component_configer.configer.value.get('proxy')
            self.proxy = process_yaml_func(proxy, component_configer.yaml_func_instance)
        if component_configer.configer.value.get("extra_headers"):
            self.ext_headers = component_configer.configer.value.get("extra_headers")
        if component_configer.configer.value.get("extra_body"):
            self.ext_params = component_configer.configer.value.get("extra_body")
        elif component_configer.configer.value.get("extra_params"):
            self.ext_params = component_configer.configer.value.get("extra_params")

        return super().initialize_by_component_configer(component_configer)

    # ---------------------------
    # token utils
    # ---------------------------
    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def max_context_length(self) -> int:
        """Return the maximum length of the context."""
        if super().max_context_length():
            return super().max_context_length()
        return 0
