# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:10
# @Author  : yuewang
# @FileName: test_node_output.py
"""Unit tests for NodeOutput."""

from agentuniverse.workflow.node.enum import NodeStatusEnum
from agentuniverse.workflow.node.node_output import NodeOutput


class TestNodeOutput:
    """Test NodeOutput defaults and field handling."""

    def test_defaults(self):
        out = NodeOutput()
        assert out.node_id is None
        assert out.result is None
        assert out.error is None
        assert out.status == NodeStatusEnum.RUNNING
        assert out.metadata is None
        assert out.edge_source_handler is None

    def test_explicit_fields(self):
        out = NodeOutput(node_id='n1', result={'a': 1}, status=NodeStatusEnum.SUCCEEDED,
                         metadata={'k': 'v'}, edge_source_handler='h')
        assert out.node_id == 'n1'
        assert out.result == {'a': 1}
        assert out.status == NodeStatusEnum.SUCCEEDED
        assert out.metadata == {'k': 'v'}

    def test_error_field(self):
        out = NodeOutput(node_id='n2', error='boom', status=NodeStatusEnum.FAILED)
        assert out.error == 'boom'
        assert out.status == NodeStatusEnum.FAILED

    def test_status_enum_covers_lifecycle(self):
        assert [s.value for s in NodeStatusEnum] == ['running', 'succeeded', 'failed']

    def test_result_accepts_arbitrary_payload(self):
        out = NodeOutput(node_id='n3', result=[{'k': 1}], status=NodeStatusEnum.SUCCEEDED)
        assert out.result == [{'k': 1}]
