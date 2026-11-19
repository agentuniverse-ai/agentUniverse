# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_node_config.py
"""Unit tests for node config parameter models."""

import pytest

from agentuniverse.workflow.node.node_config import (
    ConditionBranchParams,
    ConditionNodeInputParams,
    ConditionParams,
    EndNodeInputParams,
    InputValueParams,
    NodeInputParams,
    NodeOutputParams,
    ToolNodeInputParams,
)


class TestNodeConfigModels:
    def test_node_output_params_defaults(self):
        params = NodeOutputParams()
        assert params.name is None
        assert params.type is None
        assert params.value is None

    def test_input_value_params(self):
        value = InputValueParams(type='reference', content=['node_1', 'output'])
        assert value.type == 'reference'
        assert value.content == ['node_1', 'output']

    def test_node_input_params_nested(self):
        input_param = NodeInputParams(name='query',
                                      value={'type': 'literal', 'content': 'hi'})
        assert input_param.value.type == 'literal'
        assert input_param.value.content == 'hi'

    def test_tool_node_input_params_default_lists(self):
        params = ToolNodeInputParams()
        assert params.tool_param == []
        assert params.input_param == []

    def test_condition_branch_structure(self):
        branch = ConditionBranchParams(name='branch_a', conditions=[
            {'compare': 'equal', 'left': {'name': 'l'}, 'right': {'name': 'r'}}
        ])
        assert branch.name == 'branch_a'
        assert branch.conditions[0].compare == 'equal'

    def test_condition_node_input_params(self):
        inputs = ConditionNodeInputParams(branches=[
            {'name': 'yes', 'conditions': [ConditionParams(compare='blank')]}
        ])
        assert len(inputs.branches) == 1
        assert inputs.branches[0].conditions[0].compare == 'blank'

    def test_end_node_input_params(self):
        inputs = EndNodeInputParams(input_param=[{'name': 'x'}],
                                    prompt={'name': 'prompt', 'value': 'text'})
        assert inputs.prompt.name == 'prompt'
        assert inputs.input_param[0].name == 'x'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
