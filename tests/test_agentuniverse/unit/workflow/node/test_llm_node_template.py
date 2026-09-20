# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/20 19:30
# @FileName: test_llm_node_template.py
from unittest.mock import patch

import pytest

from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.workflow.node.llm_node import LLMNode
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


class _FakeLLM:
    """Capture the rendered messages without calling a real model."""

    def __init__(self):
        self.messages = None

    def set_by_agent_model(self, model_name=None, temperature=None):
        pass

    def call(self, messages, streaming=False):
        self.messages = messages
        return LLMOutput(text='ok')


def _build_node(template):
    return LLMNode(
        id='llm',
        data={
            'inputs': {
                'llm_param': [{'name': 'prompt', 'value': template}],
                'input_param': [
                    {
                        'name': 'value',
                        'value': {'type': 'reference', 'content': ['source', 'value']},
                    }
                ],
            },
            'outputs': [{'name': 'text', 'type': 'string'}],
        },
    )


def _workflow_output_with(value):
    workflow_output = WorkflowOutput()
    workflow_output.workflow_parameters['source'] = [
        NodeOutputParams(name='value', type='number', value=value)
    ]
    return workflow_output


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("seven", "count is seven"),
        (5, "count is 5"),
        (0, "count is 0"),
        (False, "count is False"),
        ({"a": 1}, "count is {'a': 1}"),
        (None, "count is "),
    ],
)
def test_llm_node_renders_non_string_template_values(value, expected):
    node = _build_node('count is {{value}}')
    workflow_output = _workflow_output_with(value)

    fake_llm = _FakeLLM()
    with patch('agentuniverse.workflow.node.llm_node.LLMManager') as manager:
        manager.return_value.get_instance_obj.return_value = fake_llm
        node.run(workflow_output)

    assert fake_llm.messages == [{'role': 'user', 'content': expected}]
    assert workflow_output.workflow_parameters['llm'][0].value == 'ok'


def test_llm_node_renders_mixed_type_variables_in_one_template():
    node = LLMNode(
        id='llm',
        data={
            'inputs': {
                'llm_param': [{'name': 'prompt', 'value': 'total is {{total}}, done is {{done}}'}],
                'input_param': [
                    {
                        'name': 'total',
                        'value': {'type': 'reference', 'content': ['source', 'total']},
                    },
                    {
                        'name': 'done',
                        'value': {'type': 'reference', 'content': ['source', 'done']},
                    },
                ],
            },
            'outputs': [{'name': 'text', 'type': 'string'}],
        },
    )
    workflow_output = WorkflowOutput()
    workflow_output.workflow_parameters['source'] = [
        NodeOutputParams(name='total', type='number', value=3),
        NodeOutputParams(name='done', type='boolean', value=True),
    ]

    fake_llm = _FakeLLM()
    with patch('agentuniverse.workflow.node.llm_node.LLMManager') as manager:
        manager.return_value.get_instance_obj.return_value = fake_llm
        node.run(workflow_output)

    assert fake_llm.messages == [{'role': 'user', 'content': 'total is 3, done is True'}]


def test_llm_node_reports_missing_template_variable():
    node = _build_node('count is {{value}} and ratio is {{ratio}}')
    workflow_output = _workflow_output_with(5)

    with patch('agentuniverse.workflow.node.llm_node.LLMManager') as manager:
        manager.return_value.get_instance_obj.return_value = _FakeLLM()
        with pytest.raises(ValueError, match="The variable ratio is not found"):
            node.run(workflow_output)
