# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : btlqql
# @FileName: test_stream_callback.py
"""Unit tests for the stream output callback handlers."""

import asyncio
import json
from queue import Queue

import pytest
from langchain_core.agents import AgentAction, AgentFinish

from agentuniverse.agent.plan.planner.react_planner.stream_callback import (
    InvokeCallbackHandler, OpenAIProtocolStreamOutPutCallbackHandler,
    StreamOutPutCallbackHandler,
)


class FinishWithOutput(AgentFinish):
    """AgentFinish exposing the legacy ``output`` property removed in langchain_core."""

    @property
    def output(self):
        return self.return_values["output"]


class TestStreamOutPutCallbackHandler:
    @pytest.fixture
    def queue_stream(self):
        return asyncio.Queue()

    @pytest.fixture
    def stream_handler(self, queue_stream):
        return StreamOutPutCallbackHandler(queue_stream=queue_stream)

    def test_default_agent_info_is_empty_dict(self):
        handler = StreamOutPutCallbackHandler(queue_stream=asyncio.Queue())
        assert handler.agent_info == {}

    def test_on_chain_start_returns_none(self, stream_handler):
        assert stream_handler.on_chain_start({"k": "v"}, {"input": 1}) is None

    def test_on_agent_action_enqueues_react_message(self, stream_handler, queue_stream):
        action = AgentAction(tool="search", tool_input="weather", log="look up weather")
        stream_handler.on_agent_action(action)
        message = queue_stream.get_nowait()
        assert message["type"] == "ReAct"
        assert message["data"]["output"] == "\nThought:look up weather"
        assert message["data"]["agent_info"] == {}

    def test_on_agent_finish_enqueues_react_message(self, stream_handler, queue_stream):
        finish = FinishWithOutput(return_values={"output": "done"}, log="")
        stream_handler.on_agent_finish(finish)
        message = queue_stream.get_nowait()
        assert message["type"] == "ReAct"
        assert message["data"]["output"] == "\nThought:done"


class TestOpenAIProtocolStreamOutPutCallbackHandler:
    @pytest.fixture
    def openai_handler(self):
        return OpenAIProtocolStreamOutPutCallbackHandler(queue_stream=asyncio.Queue())

    def test_default_agent_info_is_empty_dict(self):
        handler = OpenAIProtocolStreamOutPutCallbackHandler(queue_stream=asyncio.Queue())
        assert handler.agent_info == {}

    def test_add_output_stream_writes_openai_chunk(self, openai_handler):
        output_stream = Queue()
        openai_handler.add_output_stream(output_stream, "partial answer")
        payload = json.loads(output_stream.get_nowait())
        assert payload["object"] == "chat.completion.chunk"
        assert payload["choices"][0]["delta"]["content"] == "partial answer"
        assert "id" in payload

    def test_add_output_stream_ignores_falsy_stream(self, openai_handler):
        assert openai_handler.add_output_stream(None, "ignored") is None


class TestInvokeCallbackHandler:
    def test_constructor_stores_source_and_llm_name(self):
        handler = InvokeCallbackHandler(source="react_planner", llm_name="demo-llm")
        assert handler.source == "react_planner"
        assert handler.llm_name == "demo-llm"
