from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class StubAgent(Agent):
    def input_keys(self):
        return []

    def output_keys(self):
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict):
        return agent_input

    def parse_result(self, agent_result: dict):
        return agent_result


def test_generate_result_accepts_reasoning_only_chunks():
    agent = StubAgent()

    result = agent.generate_result([
        {"reasoning_content": "step"},
        {"text": "answer", "reasoning_content": None},
    ])

    assert result == {"text": "answer", "reasoning_content": "step"}
