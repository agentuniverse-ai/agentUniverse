# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: demo_agent.py

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.agent_util import assemble_memory_input, assemble_memory_output
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser

from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt

from langchain_core.output_parsers import StrOutputParser


class DemoAgent(AgentTemplate):
    """A demo agent template that wires memory, LLM, prompt, tools and knowledge.

       This agent reads the user input, optionally invokes tools and retrieves
       knowledge, then runs the prompt + LLM chain to produce a text answer.
       """

    def input_keys(self) -> list[str]:
        """Keys expected in `InputObject` for this agent.

                Returns:
                    list[str]: Required input keys. Currently only `["input"]`.
                """
        return ['input']

    def output_keys(self) -> list[str]:
        """Keys that appear in the agent's final output dictionary.

               Returns:
                   list[str]: Output keys. Currently only `["output"]`.
               """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Convert `InputObject` to the internal `agent_input` structure.

              Args:
                  input_object: Wrapped request payload.
                  agent_input: Mutable dict used as the agent's working input.

              Returns:
                  dict: The updated `agent_input`, with `"input"` populated.

              Raises:
                  KeyError: If `input_object` does not contain key `"input"`.
              """
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Adapt the internal result to the public output schema.

               Args:
                   agent_result: The dict returned by `customized_execute`.

               Returns:
                   dict: A dict including key `"output"`, merged with other fields.
               """
        return {**agent_result, 'output': agent_result['output']}

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        """The standard execution pipeline for this agent.

               Steps:
               1) Prepare memory/LLM/prompt.
               2) Optionally invoke tools.
               3) Optionally query knowledge sources.
               4) Call `customized_execute` to run chain and assemble memory.

               Args:
                   input_object: The request wrapper. Must contain `"input"`.
                   agent_input: Mutable dict carrying input/background etc.

               Returns:
                   dict: A dict with `"output"` text and intermediate fields.

               Note:
                   This method mutates `agent_input["background"]` by appending tool
                   and knowledge results, then delegates to `customized_execute`.
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
        """Run the prompt+LLM chain and manage memory IO.

                This method:
                - Writes the user input to memory (pre-call).
                - Builds a runnable chain: `prompt -> llm -> ReasoningOutputParser`.
                - Invokes chain to get the final text.
                - Writes the (human, ai) pair to memory (post-call).

                Args:
                    input_object: The incoming request wrapper.
                    agent_input: Mutable dict containing `"input"` and context fields.
                    memory: Memory component, used for conversational history.
                    llm: LLM component configured for this agent.
                    prompt: Prompt component configured for this agent.
                    **kwargs: Extra kwargs forwarded to `invoke_chain`.

                Returns:
                    dict: A dict merged from `agent_input` with an `"output"` field.

                Raises:
                    RuntimeError: If chain invocation fails.
                """
        assemble_memory_input(memory, agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | ReasoningOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        return {**agent_input, 'output': res}
