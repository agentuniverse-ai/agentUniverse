# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/12 22:54
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: insurance_agent_template.py
import json

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class InsuranceAgentTemplate(AgentTemplate):
    """Multi-agent template for the insurance product Q&A demo.
    Runs a planning agent to split the question, an executing agent to gather context, and an expressing agent to compose the final answer, each resolved by name from the profile.
    """
    planning_agent_name: str = None
    executing_agent_name: str = None
    expressing_agent_name: str = None

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Populate the agent input with the user input.
        Also queries the insurance_info_tool for the demo product description and attaches it to the input object for the sub-agents.
        """
        agent_input['input'] = input_object.get_data('input')
        detail_tool = ToolManager().get_instance_obj('insurance_info_tool')
        tool_res = detail_tool.run(ins_name='保险产品A')
        input_object.add_data('prod_description', tool_res)
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Return the agent result unchanged."""
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Run the pipeline: build the sub-agents, then invoke planning, executing and expressing in sequence.
        Returns the agent input extended with the expressing output under 'output'.
        """
        agents = self._generate_agents()

        # 1. planning agent.
        self._invoke_planning(input_object, agent_input, agents)

        # 2. executing agent.
        self._invoke_executing(input_object, agents)

        # 3. expressing agent.
        expressing_result = self._invoke_expressing(input_object, agents)

        return {**agent_input, 'output': expressing_result.get('output', '')}

    def _invoke_planning(self, input_object: InputObject, agent_input: dict, agents: dict) -> dict:
        """Run the planning agent to split the user question into sub-queries.
        Without a planning agent the original input is kept as the single sub-query; the list is stored on the input object for the executing stage.
        """
        planning_agent: Agent = agents.get('planning')
        if not planning_agent:
            planning_result = OutputObject({"sub_query_list": [agent_input.get('input')]})
            sub_query_list = [agent_input.get('input')]
        else:
            planning_result = planning_agent.run(**input_object.to_dict())
            split_questions = planning_result.get_data('planning_output')
            sub_query_list = json.loads(split_questions).get('sub_query_list')
        input_object.add_data('sub_query_list', sub_query_list)
        return planning_result.to_dict()

    def _invoke_executing(self, input_object: InputObject, agents: dict) -> dict:
        """Run the executing agent to gather search context for the sub-queries.
        Without an executing agent an empty context is used; the context is stored on the input object for the expressing stage.
        """
        executing_agent: Agent = agents.get('executing')
        if not executing_agent:
            executing_result = OutputObject({"search_context": ''})
        else:
            executing_result = executing_agent.run(**input_object.to_dict())
        input_object.add_data('search_context', executing_result.get_data('search_context'))
        return executing_result.to_dict()

    def _invoke_expressing(self, input_object: InputObject, agents: dict) -> dict:
        """Run the expressing agent to compose the final answer from the gathered context.
        Without an expressing agent an empty output is used.
        """
        expressing_agent: Agent = agents.get('expressing')
        if not expressing_agent:
            expressing_result = OutputObject({"output": ''})
        else:
            expressing_result = expressing_agent.run(**input_object.to_dict())
        return expressing_result.to_dict()

    def _generate_agents(self) -> dict:
        """Resolve the planning, executing and expressing agents by their configured names via AgentManager.

        Returns:
        dict: The agents keyed as 'planning', 'executing' and 'expressing'.
        """
        planning_agent = AgentManager().get_instance_obj(self.planning_agent_name)
        executing_agent = AgentManager().get_instance_obj(self.executing_agent_name)
        expressing_agent = AgentManager().get_instance_obj(self.expressing_agent_name)
        return {'planning': planning_agent,
                'executing': executing_agent,
                'expressing': expressing_agent}

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'InsuranceAgentTemplate':
        """Set the planning, executing and expressing agent names from the component configer profile and return this instance."""
        super().initialize_by_component_configer(component_configer)
        if self.agent_model.profile.get('planning') is not None:
            self.planning_agent_name = self.agent_model.profile.get('planning')
        if self.agent_model.profile.get('executing') is not None:
            self.executing_agent_name = self.agent_model.profile.get('executing')
        if self.agent_model.profile.get('expressing') is not None:
            self.expressing_agent_name = self.agent_model.profile.get('expressing')
        return self
