# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 18:01
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: condition_node.py
from typing import List, Optional

from agentuniverse.workflow.node.enum import NodeEnum, ConditionComparisonEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import ConditionNodeInputParams, ConditionBranchParams, ConditionParams, \
    NodeInputParams, NodeOutputParams
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
        condition_branches: List[ConditionBranchParams] = inputs.branches or []

        def resolve_value(node_input: NodeInputParams):
            if node_input.value.type == 'reference':
                reference_node_id = node_input.value.content[0]
                reference_output_params: List[NodeOutputParams] = workflow_output.workflow_parameters.get(
                    reference_node_id, [])
                return next(
                    (param.value for param in reference_output_params if param.name == node_input.value.content[1]),
                    None)
            return node_input.value.content

        def _eval_condition(condition: ConditionParams) -> bool:
            left_val = resolve_value(condition.left)
            right_val = resolve_value(condition.right) if condition.right else None
            compare: str = condition.compare
            if compare == ConditionComparisonEnum.EQUAL.value:
                return left_val == right_val
            elif compare == ConditionComparisonEnum.NOT_EQUAL.value:
                return left_val != right_val
            elif compare == ConditionComparisonEnum.BLANK.value:
                return left_val is None
            # Unknown comparator: fail closed (treat as not matching) so the
            # branch falls through to default rather than silently matching.
            return False

        # Evaluate each branch in order; a branch matches when ALL of its
        # conditions are true (AND semantics). The first matching branch
        # wins; if none match, fall through to the default edge.
        # The previous code only inspected branches[0].conditions[0], so any
        # branch beyond the first was dead configuration.
        matched_branch_name = 'branch-default'
        for condition_branch in condition_branches:
            conditions = condition_branch.conditions or []
            if conditions and all(_eval_condition(c) for c in conditions):
                matched_branch_name = condition_branch.name or 'branch-default'
                break

        return NodeOutput(
            node_id=self.id,
            status=NodeStatusEnum.SUCCEEDED,
            edge_source_handler=matched_branch_name
        )
