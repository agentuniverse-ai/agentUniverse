# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/16 15:28
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_channel.py
from typing import Optional, Any, Union, Iterator, AsyncIterator, List

import httpx
import openai
import tiktoken
from openai import OpenAI, AsyncOpenAI

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message, ToolCall, FunctionCall
from agentuniverse.base.annotation.trace import trace_llm
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.llm.llm_output import (
    LLMOutput,
    TokenUsage,
    LLMStreamEvent,
    StreamEventType,
    ToolCallDelta,
)
from agentuniverse.llm.transfer_utils import au_messages_to_openai


class LLMChannel(ComponentBase):
    channel_name: Optional[str] = None
    channel_api_key: Optional[str] = None
    channel_api_base: Optional[str] = None
    channel_organization: Optional[str] = None
    channel_proxy: Optional[str] = None
    channel_model_name: Optional[str] = None
    channel_ext_info: Optional[dict] = None
    ext_headers: Optional[dict] = {}
    ext_params: Optional[dict] = {}

    model_support_stream: Optional[bool] = None
    model_support_max_context_length: Optional[int] = None
    model_support_max_tokens: Optional[int] = None
    model_is_openai_protocol_compatible: Optional[bool] = True

    _channel_model_config: Optional[dict] = None
    client: Any = None
    async_client: Any = None
    component_type: ComponentEnum = ComponentEnum.LLM_CHANNEL

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'LLMChannel':
        super()._initialize_by_component_configer(component_configer)
        if hasattr(component_configer, "channel_name"):
            self.channel_name = component_configer.channel_name
        if hasattr(component_configer, "channel_api_key"):
            self.channel_api_key = component_configer.channel_api_key
        if hasattr(component_configer, "channel_api_base"):
            self.channel_api_base = component_configer.channel_api_base
        if hasattr(component_configer, "channel_organization"):
            self.channel_organization = component_configer.channel_organization
        if hasattr(component_configer, "channel_proxy"):
            self.channel_proxy = component_configer.channel_proxy
        if hasattr(component_configer, "channel_model_name"):
            self.channel_model_name = component_configer.channel_model_name
        if hasattr(component_configer, "channel_ext_info"):
            self.channel_ext_info = component_configer.channel_ext_info
        if hasattr(component_configer, "model_support_stream"):
            self.model_support_stream = component_configer.model_support_stream
        if hasattr(component_configer, "model_support_max_context_length"):
            self.model_support_max_context_length = component_configer.model_support_max_context_length
        if hasattr(component_configer, "model_support_max_tokens"):
            self.model_support_max_tokens = component_configer.model_support_max_tokens
        if hasattr(component_configer, "model_is_openai_protocol_compatible"):
            self.model_is_openai_protocol_compatible = component_configer.model_is_openai_protocol_compatible
        if component_configer.configer.value.get("extra_headers"):
            self.ext_headers = component_configer.configer.value.get("extra_headers", {})
        if component_configer.configer.value.get("extra_body"):
            self.ext_params = component_configer.configer.value.get("extra_body", {})
            self.ext_params["stream_options"] = {
                "include_usage": True
            }
        elif component_configer.configer.value.get("extra_params"):
            self.ext_params = component_configer.configer.value.get(
                "extra_params", {})
            self.ext_params["stream_options"] = {
                "include_usage": True
            }
        else:
            self.ext_params = {
                "stream_options": {
                    "include_usage": True
                }
            }
        return self

    def create_copy(self):
        return self

    @property
    def channel_model_config(self):
        return self._channel_model_config

    @channel_model_config.setter
    def channel_model_config(self, config: dict):
        self._channel_model_config = config
        if config:
            for key, value in config.items():
                if not isinstance(key, str):
                    continue
                if key == 'streaming':
                    if self.model_support_stream is False:
                        value = False
                if key == 'max_tokens':
                    if self.model_support_max_tokens:
                        value = min(self.model_support_max_tokens, value) if value else self.model_support_max_tokens
                if key == 'max_context_length':
                    if self.model_support_max_context_length:
                        value = min(self.model_support_max_context_length,
                                    value) if value else self.model_support_max_context_length
                if key == 'ext_params' and value and isinstance(value, dict):
                    self.ext_params.update(value)
                if key == 'ext_headers' and value and isinstance(value, dict):
                    self.ext_headers.update(value)
                if not self.__dict__.get(key):
                    self.__dict__[key] = value

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
        """Convert an OpenAI message dict to our Message type."""
        tool_calls: Optional[List[ToolCall]] = None
        function_call: Optional[FunctionCall] = None

        if msg.get("tool_calls"):
            tool_calls = []
            for i, tc in enumerate(msg.get("tool_calls") or []):
                tc = tc or {}
                if tc.get("type", "function") != "function":
                    continue
                fn = (tc.get("function") or {}) if isinstance(tc.get("function"), dict) else {}
                tool_calls.append(
                    ToolCall.create(
                        id=tc.get("id") or f"call_{i}",
                        name=fn.get("name", ""),
                        arguments=fn.get("arguments", ""),
                    )
                )

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
        """Non-streaming: build final LLMOutput with message/tool_calls/usage/finish_reason."""
        raw = self._to_dict(chat_completion)

        choices = raw.get("choices") or []
        choice0 = choices[0] if choices else {}

        msg = choice0.get("message") or {}
        content = msg.get("content")
        text = content if isinstance(content, str) else ""

        message = self._build_message_from_openai_message(msg)
        usage = TokenUsage.from_openai(raw.get("usage"))
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
        """Streaming: parse one chunk into 0..n LLMStreamEvent."""
        response_id = chunk.get("id")

        if chunk.get("usage"):
            yield LLMStreamEvent(type=StreamEventType.USAGE, usage=TokenUsage.from_openai(chunk.get("usage")))

        choices = chunk.get("choices") or []
        for choice in choices:
            choice = choice or {}
            delta = choice.get("delta") or {}

            if "content" in delta:
                c = delta.get("content")
                if c:
                    yield LLMStreamEvent.text(c)

            r = delta.get("reasoning") or delta.get("reasoning_content")
            if r:
                yield LLMStreamEvent.reasoning(r)

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

            finish_reason = choice.get("finish_reason")
            if finish_reason:
                usage_obj = TokenUsage.from_openai(chunk.get("usage")) if chunk.get("usage") else None
                yield LLMStreamEvent.done(
                    finish_reason=finish_reason,
                    usage=usage_obj,
                    response_id=response_id,
                )

    # ---------------------------
    # Public call interface
    # ---------------------------
    @trace_llm
    def call(self, *args: Any, **kwargs: Any):
        """Run the LLM."""
        return self._call(*args, **kwargs)

    @trace_llm
    async def acall(self, *args: Any, **kwargs: Any):
        """Asynchronously run the LLM."""
        return await self._acall(*args, **kwargs)

    # ---------------------------
    # Core call
    # ---------------------------
    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMStreamEvent]]:
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.channel_model_config.get('streaming')
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        if self.model_support_stream is False and streaming is True:
            streaming = False

        support_max_tokens = self.model_support_max_tokens
        max_tokens = kwargs.pop('max_tokens', None) or self.channel_model_config.get('max_tokens',
                                                                                     None) or support_max_tokens
        if support_max_tokens and max_tokens:
            max_tokens = min(support_max_tokens, max_tokens)

        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop("extra_body", {})
        ext_params = {**ext_params, **extra_body}
        if not streaming:
            ext_params.pop("stream_options", None)

        self.client = self._new_client()
        self.client.base_url = kwargs.pop('api_base') if kwargs.get('api_base') else self.channel_api_base

        openai_messages = au_messages_to_openai(messages)
        chat_completion = self.client.chat.completions.create(
            messages=openai_messages,
            model=kwargs.pop('model', self.channel_model_name),
            temperature=kwargs.pop('temperature', self.channel_model_config.get('temperature')),
            stream=kwargs.pop('stream', streaming),
            max_tokens=max_tokens,
            extra_body=ext_params,
            extra_headers=kwargs.pop("extra_headers", self.ext_headers),
            **kwargs,
        )
        if not streaming:
            return self._build_llm_output_from_chat_completion(chat_completion)
        return self.generate_stream_events(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMStreamEvent]]:
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.channel_model_config.get('streaming')
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        if self.model_support_stream is False and streaming is True:
            streaming = False

        support_max_tokens = self.model_support_max_tokens
        max_tokens = kwargs.pop('max_tokens', None) or self.channel_model_config.get('max_tokens',
                                                                                     None) or support_max_tokens
        if support_max_tokens and max_tokens:
            max_tokens = min(support_max_tokens, max_tokens)

        ext_params = self.ext_params.copy()
        extra_body = kwargs.pop("extra_body", {})
        ext_params = {**ext_params, **extra_body}
        if not streaming:
            ext_params.pop("stream_options", None)

        self.async_client = self._new_async_client()
        self.async_client.base_url = kwargs.pop('api_base') if kwargs.get('api_base') else self.channel_api_base

        openai_messages = au_messages_to_openai(messages)
        chat_completion = await self.async_client.chat.completions.create(
            messages=openai_messages,
            model=kwargs.pop('model', self.channel_model_name),
            temperature=kwargs.pop('temperature', self.channel_model_config.get('temperature')),
            stream=kwargs.pop('stream', streaming),
            max_tokens=max_tokens,
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

    async def agenerate_stream_events(self, stream: AsyncIterator) -> AsyncIterator[LLMStreamEvent]:
        """Async streaming: yield structured events."""
        try:
            async for chunk in stream:
                d = self._to_dict(chunk)
                for evt in self._iter_stream_events_from_chunk(d):
                    yield evt
        except Exception as e:
            yield LLMStreamEvent.err(str(e))

    # ---------------------------
    # Client builders
    # ---------------------------
    def _new_client(self) -> OpenAI:
        """Initialize the openai client."""
        if self.client is not None:
            return self.client
        return OpenAI(
            api_key=self.channel_api_key,
            organization=self.channel_organization,
            base_url=self.channel_api_base,
            timeout=self.channel_model_config.get('request_timeout'),
            max_retries=self.channel_model_config.get('max_retries'),
            http_client=httpx.Client(proxy=self.channel_proxy) if self.channel_proxy else None,
            **(self.channel_model_config.get('client_args') or {}),
        )

    def _new_async_client(self) -> AsyncOpenAI:
        """Initialize the openai async client."""
        if self.async_client is not None:
            return self.async_client
        return AsyncOpenAI(
            api_key=self.channel_api_key,
            organization=self.channel_organization,
            base_url=self.channel_api_base,
            timeout=self.channel_model_config.get('request_timeout'),
            max_retries=self.channel_model_config.get('max_retries'),
            http_client=httpx.AsyncClient(proxy=self.channel_proxy) if self.channel_proxy else None,
            **(self.channel_model_config.get('client_args') or {}),
        )

    # ---------------------------
    # Token utils
    # ---------------------------
    def get_num_tokens(self, text: str, model=None) -> int:
        """Get the number of tokens present in the text."""
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def max_context_length(self) -> int:
        return self.channel_model_config.get('max_context_length')

    def get_instance_code(self) -> str:
        """Return the full name of the component."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.channel_name}'
