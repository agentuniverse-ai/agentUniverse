# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 19:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node.py
from abc import abstractmethod
from typing import Optional, Dict, List, Any

from pydantic import BaseModel

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.node.node_config import NodeOutputParams, NodeInputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


class NodeData(BaseModel):
    """Data model of a workflow node holding its output parameters."""

    outputs: Optional[List[NodeOutputParams]] = None


class Node(BaseModel):
    """The basic class of the node."""

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    type: NodeEnum = None
    workflow_id: Optional[str] = None
    position: Optional[dict] = None
    _data: Optional[NodeData] = None
    _data_cls = NodeData

    def __init__(self, **kwargs):
        """Initialize the node and build its data model from the given data."""
        super().__init__(**kwargs)
        self._data = self._data_cls(**kwargs.get('data', {}))

    @abstractmethod
    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        """Execute the node logic; implemented by concrete node subclasses.

        Args:
            workflow_output: The output of the workflow being executed.

        Returns:
            The NodeOutput produced by the node.
        """
        raise NotImplementedError

    def run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        """Run the node against the given workflow output.

        Args:
            workflow_output: The output of the workflow being executed.

        Returns:
            The NodeOutput produced by the node.
        """
        return self._run(workflow_output)

    @staticmethod
    def _resolve_input_params(input_params: List[NodeInputParams],
                              workflow_output: WorkflowOutput) -> Dict[str, Any]:
        """Resolve the input parameters of the node.

        Args:
            input_params (List[NodeInputParams]): The input parameters of the node.
            workflow_output (WorkflowOutput): The output of the workflow.
        """
        node_input_params = {}
        for input_param in input_params:
            val = input_param.value
            if val.type == 'reference':
                reference_node_id = val.content[0]
                reference_output_params: List[NodeOutputParams] = workflow_output.workflow_parameters.get(
                    reference_node_id, [])
                node_input_params[input_param.name] = next(
                    (param.value for param in reference_output_params if param.name == val.content[1]), None)
            else:
                node_input_params[input_param.name] = val.content
        return node_input_params
