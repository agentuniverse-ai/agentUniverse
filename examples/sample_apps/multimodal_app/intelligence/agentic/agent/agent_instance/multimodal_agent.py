# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/19 17:58
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: multimodal_agent.py
from langchain_core.output_parsers import StrOutputParser

from agentuniverse.base.util.prompt_util import process_llm_token

from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.agent.agent import Agent

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class MultimodalAgent(Agent):

    """Demo agent that handles multimodal input.
    
        It assembles memory and prompt, invokes tools and knowledge, then runs
        the generation chain via customized_execute.
    """
    def input_keys(self) -> list[str]:
        """Return the input key names consumed by this agent.
        
        Returns:
            list[str]: The input keys.
        """
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output key names produced by this agent.
        
        Returns:
            list[str]: The output keys.
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Move the raw user input into the agent input dict.
        
        Args:
            input_object (InputObject): Parsed user input.
            agent_input (dict): Agent input dict.
        
        Returns:
            dict: Updated agent input dict.
        """
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Ensure the result dict contains the 'output' key.
        
        Args:
            agent_result (dict): Raw agent result.
        
        Returns:
            dict: Result dict including 'output'.
        """
        return {**agent_result, 'output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        """Run the full agent flow: memory, LLM, prompt, tools, knowledge and chain execution.
        
        Args:
            input_object (InputObject): Parsed user input.
            agent_input (dict): Agent input dict.
        
        Returns:
            dict: The final agent result.
        """
        memory: Memory = self.process_memory(agent_input)
        llm: LLM = self.process_llm()
        prompt: Prompt = self.process_prompt(agent_input)
        tool_res: str = self.invoke_tools(input_object)
        knowledge_res: str = self.invoke_knowledge(agent_input.get('input'), input_object)
        agent_input['background'] = (agent_input['background']
                                     + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}")
        return self.customized_execute(input_object, agent_input, memory, llm, prompt)

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        """Assemble memory around the prompt-to-LLM chain run and return the output.
        
        Args:
            input_object (InputObject): Parsed user input.
            agent_input (dict): Agent input dict.
            memory (Memory): Agent memory instance.
            llm (LLM): Language model instance.
            prompt (Prompt): Agent prompt instance.
        
        Returns:
            dict: Agent input dict with the 'output' result.
        """
        assemble_memory_input(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        return {**agent_input, 'output': res}
