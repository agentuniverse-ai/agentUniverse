# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 20:01
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_node.py
from typing import List, Optional

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import NodeData, Node
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.node.node_config import ToolNodeInputParams, NodeInfoParams, NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


class ToolNodeData(NodeData):
    inputs: Optional[ToolNodeInputParams] = None


class ToolNode(Node):
    """The basic class of the tool node."""
    _data_cls = ToolNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.TOOL

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        inputs: ToolNodeInputParams = self._data.inputs
        tool_params: List[NodeInfoParams] = inputs.tool_param
        tool_id = None
        for tool_param in tool_params:
            if tool_param.name == 'id':
                if isinstance(tool_param.value, dict):
                    tool_id = tool_param.value['content']
                else:
                    tool_id = tool_param.value
        tool: Tool = ToolManager().get_instance_obj(tool_id)
        if tool is None:
            raise ValueError("No tool with id {} was found.".format(tool_id))

        tool_input_params = self._resolve_input_params(inputs.input_param, workflow_output)
        tool_output = tool.run(**tool_input_params)
        output_params: List[NodeOutputParams] = self._data.outputs

        if isinstance(tool_output, str):
            output_params[0].value = tool_output
        elif isinstance(tool_output, dict):
            for output_param in output_params:
                output_param.value = tool_output.get(output_param.name, None)
        else:
            raise TypeError(f"The type of tool_output is not supported.")
        workflow_output.workflow_parameters[self.id] = output_params
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)
