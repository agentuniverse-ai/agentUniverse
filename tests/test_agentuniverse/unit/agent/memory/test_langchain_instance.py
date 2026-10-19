# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:50
# @Author  : yuewang
# @FileName: test_langchain_instance.py
"""Unit tests for AuConversationSummaryBufferMemory and AuConversationTokenBufferMemory."""

import pytest
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import SystemMessage

from agentuniverse.agent.memory.langchain_instance import (
    AuConversationSummaryBufferMemory,
    AuConversationTokenBufferMemory,
)
from agentuniverse.agent.memory.message import Message


class FakeLLM(BaseLanguageModel):
    """Concrete BaseLanguageModel that never exceeds the buffer limit."""

    def invoke(self, *a, **k): return ''
    def predict(self, *a, **k): return ''
    def predict_messages(self, *a, **k): return []
    async def apredict(self, *a, **k): return ''
    async def apredict_messages(self, *a, **k): return []
    def generate_prompt(self, *a, **k): return []
    async def agenerate_prompt(self, *a, **k): return []
    def get_num_tokens(self, text): return 0


def _mock_llm():
    return FakeLLM()


def _conversation():
    return [
        Message(type='system', content='sys prompt'),
        Message(type='human', content='hi there'),
        Message(type='ai', content='hello!'),
    ]


class TestAuConversationTokenBufferMemory:
    """Test the token buffer memory."""

    def test_build_memory_drops_system_message(self):
        mem = AuConversationTokenBufferMemory(llm=_mock_llm(), messages=_conversation())
        stored = mem.load_memory
        assert [m.content for m in stored] == ['hi there', 'hello!']

    def test_generate_chat_messages(self):
        mem = AuConversationTokenBufferMemory(
            llm=_mock_llm(), input_key='input', output_key='output')
        inputs, outputs = mem.generate_chat_messages(
            Message(type='human', content='q'), Message(type='ai', content='a'))
        assert inputs == {'input': 'q'}
        assert outputs == {'output': 'a'}

    def test_save_context_records_history_in_inputs(self):
        mem = AuConversationTokenBufferMemory(llm=_mock_llm())
        inputs = {'input': 'q2'}
        mem.save_context(inputs, {'output': 'a2'})
        # save_context mutates the input dict with the memory_key history
        assert 'history' in inputs
        assert inputs['history'][-1]['content'] == 'a2'


class TestAuConversationSummaryBufferMemory:
    """Test the summary buffer memory."""

    def test_system_message_moves_to_summary_buffer(self):
        mem = AuConversationSummaryBufferMemory(llm=_mock_llm(), messages=_conversation())
        assert mem.moving_summary_buffer == 'sys prompt'

    def test_load_memory_prepends_summary(self):
        mem = AuConversationSummaryBufferMemory(llm=_mock_llm(), messages=_conversation())
        loaded = mem.load_memory
        # the summary is prepended as the configured summary message class
        assert isinstance(loaded[0], SystemMessage)
        assert loaded[0].content == 'sys prompt'
        assert len(loaded) == 3



if __name__ == '__main__':
    pytest.main([__file__, '-v'])
