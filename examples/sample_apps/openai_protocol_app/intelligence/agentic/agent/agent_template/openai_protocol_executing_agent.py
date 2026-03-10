from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.executing_agent_template import ExecutingAgentTemplate
from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.llm.llm import LLM


class ExecutingOpenAIAgentTemplate(OpenAIProtocolTemplate, ExecutingAgentTemplate):
    def parse_openai_protocol_output(self, output_object: OutputObject) -> OutputObject:
        return output_object

    def input_keys(self) -> list[str]:
        return ExecutingAgentTemplate.input_keys(self)

    def output_keys(self) -> list[str]:
        return ExecutingAgentTemplate.output_keys(self)

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM,
                           agent_context: AgentContext = None, **kwargs) -> dict:
        return ExecutingAgentTemplate.customized_execute(self, input_object, agent_input, memory, llm,
                                                         agent_context=agent_context, **kwargs)

    def parse_result(self, agent_result: dict) -> dict:
        return ExecutingAgentTemplate.parse_result(self, agent_result)

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        self.add_output_stream(input_object.get_data('output_stream', None), '## Executing  \n\n')
        return ExecutingAgentTemplate.parse_input(self, input_object, agent_input)
