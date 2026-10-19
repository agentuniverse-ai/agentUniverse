# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:40
# @Author  : yuewang
# @FileName: test_stream_callback.py
"""Unit tests for the react planner stream callback handlers."""

import asyncio
import uuid
from unittest.mock import MagicMock

import pytest
from langchain_core.agents import AgentAction
from langchain_core.outputs import GenerationChunk

import agentuniverse.agent.plan.planner.react_planner.stream_callback as sc
from agentuniverse.agent.plan.planner.react_planner.stream_callback import (
    InvokeCallbackHandler,
    StreamOutPutCallbackHandler,
)

AGENT_INFO = {'name': 'agent_a'}


@pytest.fixture(autouse=True)
def patched_memory(monkeypatch):
    """Patch ConversationMemoryModule to avoid framework side effects."""
    monkeypatch.setattr(sc, 'ConversationMemoryModule', MagicMock())


def _queue():
    return asyncio.Queue()


class TestStreamOutPutCallbackHandler:
    """Test ReAct/token queue events of the stream handler."""

    def test_on_agent_finish(self):
        # the handler only reads finish.output, so a namespace is sufficient
        from types import SimpleNamespace
        q = _queue()
        handler = StreamOutPutCallbackHandler(q, agent_info=AGENT_INFO)
        handler.on_agent_finish(SimpleNamespace(output='final'))
        assert q.get_nowait()['data']['output'] == '\nThought:final'

    def test_on_tool_end_with_and_without_prefix(self):
        q = _queue()
        handler = StreamOutPutCallbackHandler(q, agent_info=AGENT_INFO)
        handler.on_tool_end('obs', observation_prefix='Obs:', run_id=uuid.uuid4(), name='t')
        assert q.get_nowait()['data']['output'] == '\nObs:obs'
        handler.on_tool_end('plain', run_id=uuid.uuid4(), name='t')
        assert q.get_nowait()['data']['output'] == '\n Observation:plain'

class TestInvokeCallbackHandler:
    """Test the LLM invoke callback handler."""

    def test_on_llm_start_records_prompt(self, patched_memory):
        handler = InvokeCallbackHandler(source='src', llm_name='llm1')
        handler.on_llm_start({}, ['p1', 'p2'], run_id=uuid.uuid4())
        call = sc.ConversationMemoryModule.return_value.add_llm_input_info.call_args
        assert call.args[0] == {'source': 'src', 'type': 'agent'}
        assert call.args[1] == 'llm1'
        assert call.args[2] == 'p1\np2'

    def test_on_llm_end_records_text(self, patched_memory):
        handler = InvokeCallbackHandler(source='src', llm_name='llm1')
        response = MagicMock()
        response.generations = [[MagicMock(text='answer')]]
        handler.on_llm_end(response, run_id=uuid.uuid4())
        call = sc.ConversationMemoryModule.return_value.add_llm_output_info.call_args
        assert call.args[2] == 'answer'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
