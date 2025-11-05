# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/20 22:10
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_node.py
import re
from typing import List, Dict

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import AgentNodeInputParams, NodeInfoParams, NodeOutputParams
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class AgentNodeData(NodeData):
    inputs: AgentNodeInputParams


class AgentNode(Node):
    """The basic class of the agent node."""

    _data_cls = AgentNodeData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = NodeEnum.AGENT

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        inputs: AgentNodeInputParams = self._data.inputs

        param_map = {
            'id': None
        }

        for agent_param in inputs.agent_param:
            if agent_param.name in param_map:
                if isinstance(agent_param.value, str):
                    param_map[agent_param.name] = agent_param.value
                else:
                    param_map[agent_param.name] = agent_param.value.get('content', None)

        agent_id = param_map['id']

        agent: Agent = AgentManager().get_instance_obj(agent_id)
        if agent is None:
            raise ValueError("No agent with id {} was found.".format(agent_id))

        agent_input_params = self._resolve_input_params(inputs.input_param, workflow_output)

        agent_output: OutputObject = agent.run(**agent_input_params)
        agent_output_dict = agent_output.to_dict()
        output_params: List[NodeOutputParams] = self._data.outputs

        for output_param in output_params:
            output_param.value = agent_output_dict.get(output_param.name, None)
        workflow_output.workflow_parameters[self.id] = output_params
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED, result=output_params)
