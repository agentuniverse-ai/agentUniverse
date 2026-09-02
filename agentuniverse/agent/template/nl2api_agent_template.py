# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/24 21:56
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: nl2api_agent_template.py
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class Nl2ApiAgentTemplate(AgentTemplate):

    """Template agent that plans API tool calls from a natural language request."""
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output key names produced by this agent.
        
        Returns:
            list[str]: The output keys.
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Populate the agent input with the raw request and the tools context.
        
        Args:
            input_object (InputObject): Parsed user input.
            agent_input (dict): Agent input dict.
        
        Returns:
            dict: Updated agent input dict.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['tools'] = self.build_tools_context()
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Ensure the result dict contains the 'output' key.
        
        Args:
            agent_result (dict): Raw agent result.
        
        Returns:
            dict: Result dict including 'output'.
        """
        return {**agent_result, 'output': agent_result['output']}

    def build_tools_context(self) -> str:
        """Build a text context describing each registered tool.
        
        Returns:
            str: Concatenated tool name and description lines.
        """
        tools_context = ''
        if self.tool_names:
            for tool_name in self.tool_names:
                tool: Tool = ToolManager().get_instance_obj(tool_name)
                tools_context += f"tool name: {tool.name}, tool description: {tool.description}\n"
        return tools_context

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'Nl2ApiAgentTemplate':
        """Initialize the agent from a component configer and set the default prompt version.
        
        Args:
            component_configer (AgentConfiger): The component configer.
        
        Returns:
            Nl2ApiAgentTemplate: The initialized agent template.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_nl2api_agent.cn')
        return self
