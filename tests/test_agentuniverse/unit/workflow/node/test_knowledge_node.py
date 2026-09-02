# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_knowledge_node.py
"""Unit tests for KnowledgeNode."""

import pytest

from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.workflow.node.enum import NodeEnum
from agentuniverse.workflow.node.knowledge_node import KnowledgeNode, KnowledgeNodeData
from agentuniverse.workflow.node.node import Node
from agentuniverse.workflow.workflow_output import WorkflowOutput


def build_node(agent_manager=None, knowledge_param=None, input_param=None, outputs=None):
    node = KnowledgeNode(
        id='kb_node',
        data={
            'inputs': {
                'knowledge_param': knowledge_param or [],
                'input_param': input_param or [],
            },
            'outputs': outputs or [{'name': 'result'}],
        },
    )
    return node


class TestKnowledgeNode:
    def test_node_type(self):
        node = KnowledgeNode(id='kb1')
        assert node.type == NodeEnum.KNOWLEDGE
        assert isinstance(node, Node)

    def test_data_class(self):
        node = build_node()
        assert isinstance(node._data, KnowledgeNodeData)

    def test_run_raises_when_knowledge_missing(self, monkeypatch):
        monkeypatch.setattr(KnowledgeManager(), 'get_instance_obj', lambda *a, **k: None)
        node = build_node(knowledge_param=[{'name': 'id', 'value': {'content': ['missing_kb']}}])
        with pytest.raises(ValueError, match='missing_kb'):
            node._run(WorkflowOutput(workflow_id='wf'))

    def test_knowledge_id_resolved_from_dict_content(self, monkeypatch):
        captured = {}

        def fake_impl(knowledge_id):
            captured['id'] = knowledge_id
            return None

        monkeypatch.setattr(KnowledgeManager(), 'get_instance_obj', fake_impl)
        node = build_node(knowledge_param=[{'name': 'id', 'value': {'content': ['dict_kb']}}])
        with pytest.raises(ValueError):
            node._run(WorkflowOutput(workflow_id='wf'))
        assert captured['id'] == 'dict_kb'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
