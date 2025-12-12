
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from langchain_core.utils.json import parse_json_markdown
from agentuniverse.base.util.common_util import stream_output
from queue import Queue
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.logging.logging_util import LOGGER

class FeedbackAgentTemplate(AgentTemplate):
    def input_keys(self) -> list[str]:
        return ['current_prompt']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['current_prompt'] = input_object.get_data('current_prompt')
        agent_input['current_performance'] = input_object.get_data('current_performance',"")
        agent_input['successful_examples'] = input_object.get_data('successful_examples',"")
        agent_input['failed_examples'] = input_object.get_data('failed_examples',"")
        agent_input['failure_analysis'] = input_object.get_data('failure_analysis',"")
        agent_input['chat_history'] = input_object.get_data('chat_history',"")
        agent_input['history_summary'] = input_object.get_data('history_summary',"")
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        llm_output = agent_result.get('output')
        parsed_result = parse_json_markdown(llm_output)
        output = parsed_result.get('output') if isinstance(parsed_result, dict) else str(parsed_result)
        logger_info = f"\nFeedback agent execution result is :\n"
        feedback_info_str = f"output: {output}\n"
        LOGGER.info(logger_info + feedback_info_str)
        return {**agent_result, 'output': output}


    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        # add scoring agent final result into the stream output.
        stream_output(output_stream,
                      {"data": {
                          'output': agent_output,
                          "agent_info": self.agent_model.info
                      }, "type": "feedback"})

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'FeedbackAgentTemplate':
        """Initialize the Agent by the AgentConfiger object.

        Args:
            component_configer(AgentConfiger): the ComponentConfiger object
        Returns:
            ScoringAgentTemplate: the ScoringAgentTemplate object
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_feedback_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                             f' is not set, please go to the agent profile configuration'
                             ' and set the `name` attribute in the `llm_model`.')
