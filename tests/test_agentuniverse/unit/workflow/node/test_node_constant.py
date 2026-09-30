# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_node_constant.py

"""Unit tests for the workflow node class mapping."""

import pytest

from agentuniverse.workflow.node import node_constant
from agentuniverse.workflow.node.agent_node import AgentNode
from agentuniverse.workflow.node.condition_node import ConditionNode
from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.knowledge_node import KnowledgeNode
from agentuniverse.workflow.node.llm_node import LLMNode
from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.node.start_node import StartNode
from agentuniverse.workflow.node.tool_node import ToolNode


class TestNodeClsMapping:
    """Test the NODE_CLS_MAPPING registry."""

    def test_expected_keys(self):
        assert set(node_constant.NODE_CLS_MAPPING.keys()) == {
            "start", "end", "tool", "knowledge", "agent", "llm", "ifelse"}

    def test_expected_classes(self):
        assert node_constant.NODE_CLS_MAPPING == {
            "start": StartNode, "end": EndNode, "tool": ToolNode,
            "knowledge": KnowledgeNode, "agent": AgentNode,
            "llm": LLMNode, "ifelse": ConditionNode}

    def test_all_values_are_node_subclasses(self):
        for cls in node_constant.NODE_CLS_MAPPING.values():
            assert issubclass(cls, Node)

    def test_lookup_by_key(self):
        assert node_constant.NODE_CLS_MAPPING["agent"] is AgentNode
        assert node_constant.NODE_CLS_MAPPING["end"] is EndNode
