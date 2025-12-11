from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from langchain_core.utils.json import parse_json_markdown


class PromptFeedbackAgentTemplate(AgentTemplate):
    def input_keys(self) -> list[str]:
        return ['current_prompt', 'evaluation_results']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['current_prompt'] = input_object.get_data('current_prompt')
        agent_input['evaluation_results'] = input_object.get_data('evaluation_results')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        llm_output = agent_result.get('output')
        parsed_result = parse_json_markdown(llm_output)
        output = parsed_result.get('output') if isinstance(parsed_result, dict) else str(parsed_result)
        return {**agent_result, 'output': output}
