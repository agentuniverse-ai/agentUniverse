# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/22 17:07
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: claude_langchain_instance.py

import warnings
from typing import List, Optional, Any

from langchain_anthropic import ChatAnthropic
from langchain_anthropic.chat_models import _tools_in_params
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.language_models.chat_models import generate_from_stream, agenerate_from_stream
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.outputs import ChatResult

from agentuniverse.llm.llm import LLM


class ClaudeLangChainInstance(ChatAnthropic):
    """
    This class wraps the Claude API into a LangChain API.
    """

    llm: LLM = None

    def __init__(self, llm: LLM):
        init_params = {}
        init_params["model"] = llm.model_name if llm.model_name else "Claude-Instant-V1.3"
        init_params["temperature"] = llm.temperature if llm.temperature else 0.7
        init_params["default_request_timeout"] = llm.request_timeout
        init_params["streaming"] = llm.streaming if llm.streaming else False
        init_params["anthropic_api_key"] = llm.api_key if llm.api_key else "blank"
        init_params["max_tokens"] = llm.max_tokens
        init_params["max_retries"] = llm.max_retries if llm.max_retries else 2
        init_params["anthropic_api_url"] = llm.api_url
        init_params["streaming"] = llm.streaming
        init_params["llm"] = llm
        super().__init__(**init_params)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if len(messages) > 1 and isinstance(messages[1], SystemMessage):
            messages[1] = HumanMessage(content=messages[1].content)
        params = self._format_params(messages=messages, stop=stop, **kwargs)
        if self.streaming:
            if _tools_in_params(params):
                warnings.warn("stream: Tool use is not yet supported in streaming mode.")
            else:
                stream_iter = self._stream(messages, stop=stop, run_manager=run_manager, **kwargs)
                return generate_from_stream(stream_iter)
        if _tools_in_params(params):
            data = self._client.beta.tools.messages.create(**params)
        else:
            data = self.llm.call(**params).raw
        return self._format_output(data, **kwargs)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if len(messages) > 1 and isinstance(messages[1], SystemMessage):
            messages[1] = HumanMessage(content=messages[1].content)
        params = self._format_params(messages=messages, stop=stop, **kwargs)
        if self.streaming:
            if _tools_in_params(params):
                warnings.warn("stream: Tool use is not yet supported in streaming mode.")
            else:
                stream_iter = self._astream(messages, stop=stop, run_manager=run_manager, **kwargs)
                return await agenerate_from_stream(stream_iter)
        if _tools_in_params(params):
            data = await self._async_client.beta.tools.messages.create(**params)
        else:
            data = await self.llm.acall(**params)
            data = data.raw
        return self._format_output(data, **kwargs)
