# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:05
# @Author  : yuewang
# @FileName: test_node.py
"""Unit tests for the base Node class."""

import pytest

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


class EchoNode(Node):
    """Concrete node that records the workflow output."""

    _data_cls = NodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.LLM

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED,
                          result=[NodeOutputParams(name='n', value='ok')])


class TestNode:
    """Test Node base behavior."""

    def test_is_abstract(self):
        with pytest.raises(TypeError):
            Node(id='x')

    def test_data_from_kwargs(self):
        node = EchoNode(id='n1', data={'inputs': {'a': 1}})
        assert isinstance(node._data, NodeData)
        assert node.id == 'n1'

    def test_run_delegates_to_run_impl(self):
        node = EchoNode(id='n2')
        out = node.run(WorkflowOutput())
        assert out.node_id == 'n2'
        assert out.status == NodeStatusEnum.SUCCEEDED

    def test_resolve_input_params_literal_and_reference(self):
        from agentuniverse.workflow.node.node_config import InputValueParams, NodeInputParams
        workflow_output = WorkflowOutput()
        workflow_output.workflow_parameters['up'] = [NodeOutputParams(name='v', value=42)]
        params = [
            NodeInputParams(name='lit', type='str',
                            value=InputValueParams(type='literal', content='x')),
            NodeInputParams(name='ref', type='str',
                            value=InputValueParams(type='reference', content=['up', 'v'])),
        ]
        assert Node._resolve_input_params(params, workflow_output) == {'lit': 'x', 'ref': 42}
