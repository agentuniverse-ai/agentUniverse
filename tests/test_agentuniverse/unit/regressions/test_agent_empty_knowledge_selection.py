from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
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


def test_explicit_empty_knowledge_list_disables_configured_sources(monkeypatch):
    class UnexpectedKnowledgeManager:
        def get_instance_obj(self, name):
            raise AssertionError("configured knowledge should be disabled")

    monkeypatch.setattr(
        "agentuniverse.agent.agent.KnowledgeManager",
        UnexpectedKnowledgeManager,
    )
    agent = StubAgent()
    agent.agent_model = AgentModel(action={"knowledge": ["configured"]})

    result = agent.invoke_knowledge(
        "question",
        InputObject({}),
        knowledge_names=[],
    )

    assert result == ""
