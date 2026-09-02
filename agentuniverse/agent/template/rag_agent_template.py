# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/24 21:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: rag_agent_template.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class RagAgentTemplate(AgentTemplate):

    """Retrieval-augmented generation (RAG) agent template.

    Invokes tool and knowledge retrieval, appends their results to the
    agent background, and delegates the final execution to the parent
    AgentTemplate implementation.
    """
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        """Output keys of the RAG agent, always ['output']."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse the raw input object into the agent input dict.

        Args:
            input_object (InputObject): raw input from the caller.
            agent_input (dict): agent input dict to fill.

        Returns:
            dict: the agent input with the 'input' field set.
        """
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the raw agent result and expose the 'output' value.

        Args:
            agent_result (dict): raw result of the agent execution.

        Returns:
            dict: result with the 'output' field set.
        """
        return {**agent_result, 'output': agent_result['output']}

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        """Execute the RAG agent synchronously after merging tool and knowledge
        results into the agent background.

        Args:
            input_object (InputObject): raw input from the caller.
            agent_input (dict): agent input dict to enrich.
        Returns:
            dict: the final agent result.
        """
        tool_res: str = self.invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}")
        return super().customized_execute(input_object, agent_input, memory, llm, prompt, **kwargs)

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM,
                                       prompt: Prompt, **kwargs) -> dict:
        """Execute the RAG agent asynchronously after merging tool and knowledge
        results into the agent background.

        Args:
            input_object (InputObject): raw input from the caller.
            agent_input (dict): agent input dict to enrich.
        Returns:
            dict: the final agent result.
        """
        tool_res: str = await self.async_invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}")
        return await super().customized_async_execute(input_object, agent_input, memory, llm, prompt, **kwargs)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'RagAgentTemplate':
        """Initialize the RAG agent from a component configer.

        Args:
            component_configer (AgentConfiger): the agent component configer.

        Returns:
            RagAgentTemplate: the initialized agent template.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_rag_agent.cn')
        return self
