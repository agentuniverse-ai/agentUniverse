from copy import deepcopy

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject


class _StubAgent(Agent):
    def input_keys(self) -> list[str]:
        return []

    def output_keys(self) -> list[str]:
        return []

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return agent_result


def test_process_prompt_preserves_agent_input_for_repeated_calls():
    agent = _StubAgent()
    agent.agent_model = AgentModel(
        profile={
            "introduction": "Introduction",
            "target": "Target",
            "instruction": "Instruction",
        }
    )
    agent_input = {
        "expert_framework": "Expert framework: ",
        "image_urls": [{"url": "https://example.com/image.png"}],
        "audio_url": "https://example.com/audio.mp3",
        "input": "Question",
    }
    original_input = deepcopy(agent_input)

    first_prompt = agent.process_prompt(agent_input)
    second_prompt = agent.process_prompt(agent_input)

    assert agent_input == original_input
    assert first_prompt.messages == second_prompt.messages


def test_generate_result_returns_empty_text_for_empty_stream():
    agent = _StubAgent()

    assert agent.generate_result([]) == ""
