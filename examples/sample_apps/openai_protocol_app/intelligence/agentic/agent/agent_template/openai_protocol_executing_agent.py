from queue import Queue
from typing import Any

from langchain_core.runnables import RunnableSerializable

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import ExecutingAgentTemplate
from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class ExecutingOpenAIAgentTemplate(OpenAIProtocolTemplate, ExecutingAgentTemplate):
    """Executing agent template adapted to the OpenAI chat protocol.

    Sub-tasks of the planning framework are executed through the standard
    executing-agent pipeline while the response is streamed back in the
    OpenAI-protocol chunk format.
    """

    def parse_openai_protocol_output(self, output_object: OutputObject) -> OutputObject:
        """Keep the executing result untouched for protocol formatting.

        Args:
            output_object (OutputObject): agent execution result.
        Returns:
            OutputObject: the same output object, unmodified.
        """
        return output_object

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        """Execute the sub-tasks stored in the planning framework.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input prepared by the framework.
            memory (Memory): agent memory instance.
            llm (LLM): llm instance used by the agent.
            prompt (Prompt): prompt instance used by the agent.
        Returns:
            dict: dict containing the ``executing_result`` and output stream.
        """
        return ExecutingAgentTemplate.customized_execute(self, input_object, agent_input, memory, llm, prompt, **kwargs)

    def invoke_chain(self, chain: RunnableSerializable[Any, str], agent_input: dict, input_object: InputObject,
                     **kwargs):
        """Invoke or stream the LLM chain and forward streamed tokens.

        When the chain supports streaming, each chunk is collected and the
        assembled answer is pushed to the OpenAI-protocol output stream.

        Args:
            chain (RunnableSerializable): langchain runnable to invoke.
            agent_input (dict): agent input prepared by the framework.
            input_object (InputObject): input parameters passed by the user.
        Returns:
            The invocation result of the chain, or the generated answer.
        """
        if not self.judge_chain_stream(chain):
            res = chain.invoke(input=agent_input, config=self.get_run_config())
            return res
        result = []
        for token in chain.stream(input=agent_input, config=self.get_run_config()):
            result.append(token)
        input = agent_input.get('input')
        self.add_output_stream(input_object.get_data('output_stream', None),
                               f'#### Question:{input} \n\n Answer: {self.generate_result(result)}\n\n')
        return self.generate_result(result)

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse the input object and announce the executing phase.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input prepared by the framework.
        Returns:
            dict: agent input parsed from ``input_object``.
        """
        self.add_output_stream(input_object.get_data('output_stream', None), '## Executing  \n\n')
        return super().parse_input(input_object, agent_input)
