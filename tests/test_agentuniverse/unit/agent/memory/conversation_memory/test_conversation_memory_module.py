# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_conversation_memory_module.py
"""Unit tests for the pure trace-relation string helpers in ConversationMemoryModule."""

import pytest

from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import (
    generate_relation_str,
    generate_relation_str_en,
)


class TestGenerateRelationStr:
    """Test generate_relation_str / generate_relation_str_en (offline, pure)."""

    def test_cn_agent_to_agent_relations(self):
        """Chinese strings for agent-agent input and output relations."""
        assert generate_relation_str("a", "b", "agent", "agent", "input") == "智能体 a 向智能体 b 提出了一个问题"
        assert generate_relation_str("a", "b", "agent", "agent", "output") == "智能体 b 回答了智能体 a 的问题"

    def test_cn_agent_to_tool_and_knowledge_relations(self):
        """Chinese strings for agent-tool and agent-knowledge relations."""
        assert generate_relation_str("a", "t", "agent", "tool", "input") == "智能体 a 调用了工具 t，执行的参数是"
        assert generate_relation_str("a", "t", "agent", "tool", "output") == "工具 t 返回给智能体 a 的执行结果"
        assert generate_relation_str("a", "k", "agent", "knowledge", "output") == "知识库 k 返回给智能体 a 的搜索结果"

    def test_cn_agent_to_llm_and_user_relations(self):
        """Chinese strings for agent-llm and user-agent relations."""
        assert generate_relation_str("a", "l", "agent", "llm", "input") == "智能体 a 向大模型 l 提问"
        assert generate_relation_str("u", "b", "user", "agent", "input") == "用户向智能体 b 提出了一个问题"
        assert generate_relation_str("u", "b", "user", "agent", "output") == "智能体 b 回答了用户的问题"

    def test_cn_unknown_and_fallback_relations(self):
        """Chinese strings for unknown sources, fallbacks and summaries."""
        assert generate_relation_str("x", "b", "unknown", "agent", "input") == "未知类型 x 向智能体 b 提出了一个问题"
        assert generate_relation_str("t", "l", "tool", "llm", "input") == "t 向 l 询问了一个问题"
        assert generate_relation_str("t", "l", "tool", "llm", "output") == "t 回答了 l 的问题"
        assert generate_relation_str("a", "t", "agent", "tool", "summary") == "a 的摘要"

    def test_cn_unsupported_type_returns_none(self):
        """Unsupported relation types produce no Chinese string."""
        assert generate_relation_str("a", "b", "agent", "agent", "plan") is None
        assert generate_relation_str("u", "b", "user", "agent", "plan") is None

    def test_en_agent_to_agent_and_tool_relations(self):
        """English strings for agent-agent and agent-tool relations."""
        assert generate_relation_str_en("a", "b", "agent", "agent", "input") == "Agent a asked a question to agent b"
        assert generate_relation_str_en("a", "b", "agent", "agent", "output") == \
            "Agent b answered the question asked by agent a"
        assert generate_relation_str_en("a", "t", "agent", "tool", "input") == \
            "Agent a called tool t, the parameters are"
        assert generate_relation_str_en("a", "t", "agent", "tool", "output") == "Tool t returned the result to agent a"

    def test_en_agent_to_knowledge_and_llm_relations(self):
        """English strings for agent-knowledge and agent-llm relations."""
        assert generate_relation_str_en("a", "k", "agent", "knowledge", "output") == \
            "Knowledge k returned the result to agent k"
        assert generate_relation_str_en("a", "l", "agent", "llm", "input") == "Agent a asked a question to llm l"
        assert generate_relation_str_en("a", "l", "agent", "llm", "output") == "LLM l returned the answer to agent a"

    def test_en_unknown_user_and_fallback_relations(self):
        """English strings for unknown/user sources, fallbacks and summaries."""
        assert generate_relation_str_en("x", "b", "unknown", "agent", "input") == \
            "Unknown type x asked a question to agent b"
        assert generate_relation_str_en("u", "b", "user", "agent", "input") == "User asked a question to agent b"
        assert generate_relation_str_en("u", "b", "user", "agent", "output") == \
            "Agent b answered the user's question"
        assert generate_relation_str_en("t", "l", "tool", "llm", "input") == "t asked a question to l"
        assert generate_relation_str_en("a", "t", "agent", "tool", "summary") == "a summary"
        assert generate_relation_str_en("a", "b", "agent", "agent", "plan") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
