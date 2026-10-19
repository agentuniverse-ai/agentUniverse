from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate


class ReviewingOpenAIAgentTemplate(OpenAIProtocolTemplate, ReviewingAgentTemplate):
    """OpenAI-protocol agent template for reviewing tasks.

    Combines the OpenAI chat protocol with reviewing-agent behavior so a
    reviewing run can be served through an OpenAI-compatible interface while
    its progress is streamed to the caller.
    """

    def parse_openai_protocol_output(self, output_object: OutputObject) -> OutputObject:
        """Keep the reviewing output object untouched.

        Args:
            output_object (OutputObject): The agent's raw result.

        Returns:
            OutputObject: The same output object, without reshaping it into
            the standard OpenAI chat.completion payload.
        """
        return output_object

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Prepare agent input and stream a reviewing heading.

        Emits a '## Reviewing' chunk on the caller's output stream (when one
        is present) and delegates the remaining input preparation to the
        reviewing template.

        Args:
            input_object (InputObject): The original input object.
            agent_input (dict): The agent input dict being built.

        Returns:
            dict: The prepared agent input dict.
        """
        self.add_output_stream(input_object.get_data('output_stream', None), '## Reviewing \n\n')
        return super().parse_input(input_object, agent_input)