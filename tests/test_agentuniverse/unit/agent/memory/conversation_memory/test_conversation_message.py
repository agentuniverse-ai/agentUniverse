# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:00
# @Author  : yuewang
# @FileName: test_conversation_message.py
"""Unit tests for ConversationMessage."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.enum import (
    ConversationMessageEnum,
    ConversationMessageSourceType,
)
from agentuniverse.agent.memory.message import Message


def _cm(type_, content='hello', **kwargs):
    return ConversationMessage(type=type_, content=content, **kwargs)


class TestConversationMessageConversion:
    """Test conversion between ConversationMessage and langchain messages."""

    def test_as_langchain_input_maps_to_human(self):
        msg = _cm(ConversationMessageEnum.INPUT.value, 'hi')
        assert isinstance(msg.as_langchain(), HumanMessage)
        assert msg.as_langchain().content == 'hi'

    def test_as_langchain_output_maps_to_ai(self):
        msg = _cm(ConversationMessageEnum.OUTPUT.value, 'answer')
        assert isinstance(msg.as_langchain(), AIMessage)
        assert msg.as_langchain().content == 'answer'

    def test_as_langchain_system(self):
        msg = _cm('system', 'sys')
        assert isinstance(msg.as_langchain(), SystemMessage)

    def test_as_langchain_unknown_type_raises(self):
        # unknown type falls back to abstract BaseStringMessagePromptTemplate
        msg = _cm('custom_type', 'tpl')
        with pytest.raises(TypeError):
            msg.as_langchain()

    def test_as_langchain_list_keeps_agent_conversations(self):
        msgs = [
            _cm('system', 'sys'),
            _cm(ConversationMessageEnum.OUTPUT.value, 'out',
                source_type='agent', target_type='agent'),
            _cm(ConversationMessageEnum.INPUT.value, 'in',
                source_type='user', target_type='agent'),
            _cm(ConversationMessageEnum.OUTPUT.value, 'tool_out',
                source_type='tool', target_type='tool'),
        ]
        result = ConversationMessage.as_langchain_list(msgs)
        # system, agent output, user input kept; tool/tool dropped
        assert len(result) == 3
        assert isinstance(result[0], SystemMessage)
        assert isinstance(result[1], AIMessage)
        assert isinstance(result[2], HumanMessage)


class TestConversationMessageFromMessage:
    """Test from_message and check_and_convert_message."""

    def test_from_message_summarize_prefix(self):
        msg = Message(type='summarize', content='summary text',
                      source='agent_a',
                      metadata={'trace_id': 't1', 'session_id': 'old'})
        cm = ConversationMessage.from_message(msg, 'new_session')
        assert cm.source_type == 'agent'
        assert cm.target_type == 'agent'
        assert cm.conversation_id == 'new_session'
        assert cm.trace_id == 't1'
        assert cm.metadata['prefix'] == '之前对话的摘要：'
        assert cm.metadata['params'] == '{}'

    def test_from_message_plain_type_empty_prefix(self):
        msg = Message(type='chat', content='c', source='agent_b',
                      metadata={'trace_id': 't2'})
        cm = ConversationMessage.from_message(msg, None)
        assert cm.metadata['prefix'] == ''
        assert cm.conversation_id is None

    def test_check_and_convert_message_passthrough_and_conversion(self):
        assert ConversationMessage.check_and_convert_message([]) == []
        cm = _cm('system', 'x')
        assert ConversationMessage.check_and_convert_message([cm]) == [cm]
        converted = ConversationMessage.check_and_convert_message(
            [Message(type='chat', content='c', metadata={'trace_id': 't'})],
            session_id='s1')
        assert len(converted) == 1
        assert isinstance(converted[0], ConversationMessage)
        assert converted[0].conversation_id == 's1'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
