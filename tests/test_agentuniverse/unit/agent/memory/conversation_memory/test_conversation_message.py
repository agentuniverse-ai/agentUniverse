# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08 10:00
# @Author  : test
# @FileName: test_conversation_message.py
"""Unit tests for the ConversationMessage model."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message


class TestConversationMessage:
    """Tests for ConversationMessage."""

    @pytest.fixture
    def output_message(self):
        return ConversationMessage(id="msg-output", type="output", source="agent_a",
                                   source_type="agent", target="agent_b",
                                   target_type="agent", content="hello world", metadata={})

    def test_field_defaults(self):
        msg = ConversationMessage()
        assert isinstance(msg.id, str) and len(msg.id) == 32
        assert msg.model_dump(exclude_none=True) == {"id": msg.id, "additional_args": {}}

    def test_constructor_kwargs(self):
        msg = ConversationMessage(id="m1", trace_id="t-1", conversation_id="c1", source="a",
                                  source_type="agent", target="b", target_type="agent",
                                  type="output", content="hi", metadata={"prefix": ""})
        assert (msg.id, msg.trace_id, msg.conversation_id) == ("m1", "t-1", "c1")
        assert (msg.source, msg.source_type, msg.target, msg.target_type) == ("a", "agent", "b", "agent")
        assert (msg.type, msg.content, msg.metadata) == ("output", "hi", {"prefix": ""})

    def test_as_langchain_mappings(self):
        cases = [("input", HumanMessage, "ask"), ("output", AIMessage, "answer"),
                 (ChatMessageEnum.SYSTEM.value, SystemMessage, "sys"),
                 (ChatMessageEnum.HUMAN.value, HumanMessage, "human"),
                 (ChatMessageEnum.AI.value, AIMessage, "ai")]
        for msg_type, lc_class, content in cases:
            converted = ConversationMessage(type=msg_type, content=content, metadata={}).as_langchain()
            assert isinstance(converted, lc_class) and converted.content == content

    def test_as_langchain_list_filtering(self, output_message):
        user_out = ConversationMessage(id="m3", type="output", source="user", source_type="user",
                                       target="agent_b", target_type="agent", content="skip", metadata={})
        tool_in = ConversationMessage(id="m4", type="input", source="tool", source_type="tool",
                                      target="agent_b", target_type="agent", content="skip", metadata={})
        kept_msgs = [output_message,
                     ConversationMessage(id="m2", type="input", source="user", source_type="user",
                                         target="agent_b", target_type="agent", content="q", metadata={}),
                     ConversationMessage(id="s1", type=ChatMessageEnum.SYSTEM.value, content="sys", metadata={})]
        converted = ConversationMessage.as_langchain_list(kept_msgs + [user_out, tool_in])
        assert [(type(item), item.content) for item in converted] == \
            [(AIMessage, "hello world"), (HumanMessage, "q"), (SystemMessage, "sys")]

    def test_from_dict(self):
        data = {"id": "d1", "type": "output", "content": "c", "source": "s",
                "source_type": "agent", "target_type": "agent", "metadata": {}}
        msg = ConversationMessage.from_dict(data)
        assert isinstance(msg, ConversationMessage)
        assert (msg.id, msg.type, msg.content) == ("d1", "output", "c")
        assert (msg.source, msg.source_type, msg.target_type) == ("s", "agent", "agent")

    def test_from_message_conversion(self):
        plain = Message(id="p1", type="human", content="plain hello", source="srv",
                        metadata={"trace_id": "tr-1"})
        msg = ConversationMessage.from_message(plain, session_id="s1")
        assert isinstance(msg, ConversationMessage)
        assert (msg.content, msg.type, msg.trace_id) == ("plain hello", "human", "tr-1")
        assert (msg.source, msg.target, msg.source_type, msg.target_type) == ("srv", "srv", "agent", "agent")
        assert (msg.conversation_id, msg.metadata["prefix"]) == ("s1", "")
        summ = Message(id="p2", type="summarize", content="summary",
                       metadata={"trace_id": "tr-2"})
        summ_msg = ConversationMessage.from_message(summ, session_id="s2")
        assert (summ_msg.metadata["prefix"], summ_msg.metadata["params"],
                summ_msg.conversation_id) == ("之前对话的摘要：", "{}", "s2")

    def test_check_and_convert_message(self, output_message):
        assert ConversationMessage.check_and_convert_message([], "s1") == []
        passed = ConversationMessage.check_and_convert_message([output_message], "s1")
        assert passed[0] is output_message
        plain = Message(id="p3", type="output", content="x", metadata={"trace_id": "tr-3"})
        converted = ConversationMessage.check_and_convert_message([plain], "s1")
        assert isinstance(converted[0], ConversationMessage)
        assert converted[0].conversation_id == "s1"
