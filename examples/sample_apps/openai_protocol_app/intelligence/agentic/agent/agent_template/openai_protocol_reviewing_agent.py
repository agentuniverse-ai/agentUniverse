from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate


class ReviewingOpenAIAgentTemplate(OpenAIProtocolTemplate, ReviewingAgentTemplate):
    def parse_openai_protocol_output(self, output_object: OutputObject) -> OutputObject:
        return output_object

    def input_keys(self) -> list[str]:
        return ReviewingAgentTemplate.input_keys(self)

    def output_keys(self) -> list[str]:
        return ReviewingAgentTemplate.output_keys(self)

    def parse_result(self, agent_result: dict) -> dict:
        return ReviewingAgentTemplate.parse_result(self, agent_result)

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        self.add_output_stream(input_object.get_data('output_stream', None), '## Reviewing \n\n')
        return ReviewingAgentTemplate.parse_input(self, input_object, agent_input)
