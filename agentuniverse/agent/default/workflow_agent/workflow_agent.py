# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 15:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_agent.py
from typing import Optional

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.workflow.workflow import Workflow
from agentuniverse.workflow.workflow_manager import WorkflowManager
from agentuniverse.workflow.workflow_output import WorkflowOutput


class WorkflowAgent(Agent):
    """Workflow Agent class."""
    workflow_id: Optional[str] = None

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return []

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Agent result parser.

        Args:
            agent_result(dict): The raw result of the agent.
        Returns:
            dict: The parsed result of the agent
        """
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        workflow: Workflow = WorkflowManager().get_instance_obj(self.workflow_id)
        # build and run workflow
        if not workflow or workflow.graph_config is None:
            raise Exception('Workflow graph is None, please add nodes and edges to the workflow graph.')
        workflow = workflow.build()
        workflow_output: WorkflowOutput = workflow.run(input_object.to_dict())
        print(workflow_output.workflow_node_results)
        return workflow_output.workflow_end_params

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'WorkflowAgent':
        super().initialize_by_component_configer(component_configer)
        self.workflow_id = (self.agent_model.profile.get('workflow_id')
                            or self.agent_model.plan.get('planner', {}).get('workflow_id'))
        return self
