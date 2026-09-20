# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/20 19:45
# @FileName: test_knowledge_node_result.py
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agentuniverse.workflow.node.knowledge_node import KnowledgeNode
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


class _FakeKnowledge:
    """Return a fixed list of documents for every query."""

    def __init__(self, document_texts):
        self._document_texts = document_texts
        self.queries = []

    def query_knowledge(self, **kwargs):
        self.queries.append(kwargs)
        return [SimpleNamespace(text=text) for text in self._document_texts]


def _build_node(knowledge_ids):
    return KnowledgeNode(
        id='knowledge',
        data={
            'inputs': {
                'knowledge_param': [
                    {
                        'name': 'id',
                        'value': {'type': 'input', 'content': knowledge_ids},
                    }
                ],
                'input_param': [
                    {
                        'name': 'query',
                        'value': {'type': 'input', 'content': 'what is agentuniverse'},
                    }
                ],
            },
            'outputs': [{'name': 'text', 'type': 'string'}],
        },
    )


def _run_node(knowledge_docs):
    """Run a knowledge node over {knowledge_id: [document texts]} and return its output value."""
    node = _build_node(list(knowledge_docs))
    knowledges = {kid: _FakeKnowledge(texts) for kid, texts in knowledge_docs.items()}
    workflow_output = WorkflowOutput()

    with patch('agentuniverse.workflow.node.knowledge_node.KnowledgeManager') as manager:
        manager.return_value.get_instance_obj.side_effect = \
            lambda knowledge_id: knowledges.get(knowledge_id)
        node.run(workflow_output)

    for knowledge in knowledges.values():
        assert knowledge.queries == [{'query_str': 'what is agentuniverse'}]
    return workflow_output.workflow_parameters['knowledge'][0].value


def test_single_knowledge_single_document_is_unchanged():
    assert _run_node({'k1': ['docA1']}) == 'docA1'


def test_single_knowledge_documents_stay_newline_separated():
    assert _run_node({'k1': ['docA1', 'docA2']}) == 'docA1\ndocA2'


def test_documents_of_different_knowledges_are_separated():
    assert _run_node({'k1': ['docA1'], 'k2': ['docB1']}) == 'docA1\ndocB1'


def test_multiple_knowledges_and_documents_join_cleanly():
    assert _run_node({'k1': ['docA1', 'docA2'], 'k2': ['docB1']}) == 'docA1\ndocA2\ndocB1'


def test_knowledge_without_matches_contributes_no_blank_segment():
    assert _run_node({'k1': [], 'k2': ['docB1']}) == 'docB1'
    assert _run_node({'k1': [], 'k2': []}) == ''


def test_unknown_knowledge_id_is_reported():
    node = _build_node(['k2'])
    with patch('agentuniverse.workflow.node.knowledge_node.KnowledgeManager') as manager:
        manager.return_value.get_instance_obj.return_value = None
        with pytest.raises(ValueError, match='No knowledge with id k2 was found'):
            node.run(WorkflowOutput())
