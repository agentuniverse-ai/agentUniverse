from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate


class CritiqueAgentTemplate(AgentTemplate):
    def input_keys(self) -> list[str]:
        pass

    def output_keys(self) -> list[str]:
        pass

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        pass

    def parse_result(self, agent_result: dict) -> dict:
        pass