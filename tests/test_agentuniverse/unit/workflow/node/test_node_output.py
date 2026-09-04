# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_node_output.py

"""Unit tests for the NodeOutput model."""

from agentuniverse.workflow.node.enum import NodeStatusEnum
from agentuniverse.workflow.node.node_output import NodeOutput


class TestNodeOutput:
    """Test NodeOutput defaults and construction."""

    def test_default_values(self):
        output = NodeOutput()
        assert output.node_id is None
        assert output.result is None
        assert output.error is None
        assert output.status == NodeStatusEnum.RUNNING
        assert output.metadata is None
        assert output.edge_source_handler is None

    def test_full_construction(self):
        output = NodeOutput(node_id="n1", result={"value": 1},
                            error=None, status=NodeStatusEnum.SUCCEEDED,
                            metadata={"k": "v"}, edge_source_handler="h")
        assert output.node_id == "n1"
        assert output.result == {"value": 1}
        assert output.status == NodeStatusEnum.SUCCEEDED
        assert output.metadata == {"k": "v"}
        assert output.edge_source_handler == "h"

    def test_failed_status_construction(self):
        output = NodeOutput(node_id="n1", status=NodeStatusEnum.FAILED,
                            error="boom")
        assert output.status == NodeStatusEnum.FAILED
        assert output.error == "boom"

    def test_equality(self):
        assert NodeOutput(node_id="a") == NodeOutput(node_id="a")
        assert NodeOutput(node_id="a") != NodeOutput(node_id="b")
