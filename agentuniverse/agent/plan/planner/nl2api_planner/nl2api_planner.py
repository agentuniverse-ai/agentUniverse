# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/18 10:50
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: nl2api_planner.py
"""Expressing planner module."""
from langchain.tools import Tool as LangchainTool
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class Nl2ApiPlanner(Planner):
    """Expressing planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        memory: Memory = self.handle_memory(agent_model, planner_input)

        llm: LLM = self.handle_llm(agent_model)

        prompt: Prompt = self.handle_prompt(agent_model, planner_input)

        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)

        assemble_memory_input(memory, planner_input)

        chain = prompt.as_langchain() | llm.as_langchain_runnable(agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(agent_model, chain, planner_input, None, input_object)

        assemble_memory_output(memory=memory,
                               agent_input=planner_input,
                               content=f"Human: {planner_input.get(self.input_key)}, AI: {res}")
        return {**planner_input, self.output_key: res}

    @staticmethod
    def acquire_tools(action) -> list[LangchainTool]:
        tool_names: list = action.get('tool') or list()
        lc_tools: list[LangchainTool] = list()
        for tool_name in tool_names:
            tool: Tool = ToolManager().get_instance_obj(tool_name)
            lc_tools.append(tool.as_langchain())
        return lc_tools

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict) -> Prompt:
        """
        Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            ChatPrompt: The chat prompt instance.
        """
        tools = self.acquire_tools(action=agent_model.action)
        lc_tools_str: str = ''
        for lc_tool in tools:
            lc_tools_str += "tool name:" + lc_tool.name + " " + "tool description:" + lc_tool.description + '\n'
        lc_tool_names = "|".join([lc_tool.name for lc_tool in tools])
        planner_input['tool_names'] = lc_tool_names
        planner_input['tools'] = lc_tools_str
        planner_input['agent_scratchpad'] = ''
        #
        profile: dict = agent_model.profile
        #
        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile.get('instruction'))

        # get the prompt by the prompt version
        prompt_version: str = profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        prompt = Prompt().build_prompt(profile_prompt_model, self.prompt_assemble_order)
        return prompt
