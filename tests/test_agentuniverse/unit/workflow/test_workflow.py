# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_workflow.py
"""Unit tests for the Workflow class."""

import pytest

from agentuniverse.workflow.workflow import Workflow


SIMPLE_GRAPH = {
    'nodes': [
        {'id': 'start', 'type': 'start', 'outputs': [{'name': 'input'}]},
        {'id': 'end', 'type': 'end', 'inputs': {'prompt': {'name': 'prompt', 'value': 'ok'}},
         'outputs': [{'name': 'result'}]},
    ],
    'edges': [
        {'source_node_id': 'start', 'target_node_id': 'end'},
    ],
}


class TestWorkflow:
    def test_default_fields_none(self):
        workflow = Workflow()
        assert workflow.id is None
        assert workflow.name is None
        assert workflow.description is None
        assert workflow.graph is None

    def test_constructor_fields(self):
        workflow = Workflow(id='wf_a', name='flow', description='desc')
        assert workflow.id == 'wf_a'
        assert workflow.name == 'flow'
        assert workflow.description == 'desc'

    def test_build_without_config_raises(self):
        workflow = Workflow()
        with pytest.raises(ValueError, match='graph config is None'):
            workflow.build()

    def test_build_builds_graph(self):
        workflow = Workflow(id='wf_b', graph_config=SIMPLE_GRAPH)
        workflow.build()
        assert workflow.graph is not None
        assert len(list(workflow.graph.nodes)) == 2

    def test_run_without_graph_raises(self):
        workflow = Workflow(id='wf_c')
        with pytest.raises(ValueError, match='graph of the workflow is None'):
            workflow.run({'input': 'x'})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
