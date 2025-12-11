from agentuniverse.agent.action.knowledge.store.faiss_store import logger
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate


class AnswerAgentTemplate(AgentTemplate):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        logger.info(f"AnswerAgentTemplate parse_result: {agent_result['output']}")
        return {**agent_result, 'output': agent_result['output']}
