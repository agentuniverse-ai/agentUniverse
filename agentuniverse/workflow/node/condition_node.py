# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 18:01
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: condition_node.py
from typing import List, Optional

from agentuniverse.workflow.node.enum import NodeEnum, ConditionComparisonEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import (
    ConditionNodeInputParams,
    ConditionBranchParams,
    ConditionParams,
    NodeInputParams,
    NodeOutputParams,
)
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class ConditionNodeData(NodeData):
    inputs: Optional[ConditionNodeInputParams] = None


class ConditionNode(Node):
    """The basic class of the condition node."""

    _data_cls = ConditionNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.CONDITION

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        inputs: ConditionNodeInputParams = self._data.inputs
        condition_branches: List[ConditionBranchParams] = inputs.branches
        condition_branch: ConditionBranchParams = condition_branches[0]
        condition: ConditionParams = condition_branch.conditions[0]

        def resolve_value(node_input: NodeInputParams):
            if node_input.value.type == "reference":
                reference_node_id = node_input.value.content[0]
                reference_output_params: List[NodeOutputParams] = workflow_output.workflow_parameters.get(
                    reference_node_id, []
                )
                return next(
                    (param.value for param in reference_output_params if param.name == node_input.value.content[1]),
                    None,
                )
            return node_input.value.content

        left_val = resolve_value(condition.left)
        right_val = resolve_value(condition.right) if condition.right else None

        compare: str = condition.compare
        res = False

        if compare == ConditionComparisonEnum.EQUAL.value:
            res = left_val == right_val
        elif compare == ConditionComparisonEnum.NOT_EQUAL.value:
            res = left_val != right_val
        elif compare == ConditionComparisonEnum.BLANK.value:
            res = left_val is None
        return NodeOutput(
            node_id=self.id,
            status=NodeStatusEnum.SUCCEEDED,
            edge_source_handler=condition_branch.name if res else "branch-default",
        )
