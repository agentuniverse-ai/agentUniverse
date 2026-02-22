from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.expressing_agent_template import ExpressingAgentTemplate
from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate


class OpenAIProtocolExpressingAgentTemplate(OpenAIProtocolTemplate, ExpressingAgentTemplate):
    def parse_openai_protocol_output(self, output_object: OutputObject) -> OutputObject:
        return output_object

    def input_keys(self) -> list[str]:
        return ExpressingAgentTemplate.input_keys(self)

    def output_keys(self) -> list[str]:
        return ExpressingAgentTemplate.output_keys(self)

    def parse_result(self, agent_result: dict) -> dict:
        return ExpressingAgentTemplate.parse_result(self, agent_result)

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        self.add_output_stream(input_object.get_data('output_stream', None), '## Expressing  \n\n')
        return ExpressingAgentTemplate.parse_input(self, input_object, agent_input)
