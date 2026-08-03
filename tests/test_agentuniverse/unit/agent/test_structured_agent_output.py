import asyncio

import pytest
from pydantic import BaseModel, Field, ValidationError

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject


class _Answer(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    sources: list[str] = []


class _StructuredAgent(Agent):
    raw_result: dict = Field(default_factory=dict)

    def input_keys(self) -> list[str]:
        return []

    def output_keys(self) -> list[str]:
        return ["answer", "confidence", "sources"]

    def output_model(self) -> type[BaseModel]:
        return _Answer

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return agent_result

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        return self.raw_result

    async def async_execute(self, input_object: InputObject, agent_input: dict) -> dict:
        return self.raw_result


def _agent(agent_cls=_StructuredAgent, **raw_result):
    agent = agent_cls()
    agent.agent_model = AgentModel(info={})
    agent.raw_result = raw_result
    return agent


def test_run_validates_and_normalizes_structured_output():
    agent = _agent(answer="ok", confidence="0.8")

    result = Agent.run.__wrapped__(agent)

    assert result.to_dict() == {
        "answer": "ok",
        "confidence": 0.8,
        "sources": [],
    }


def test_async_run_uses_the_same_structured_output_contract():
    agent = _agent(answer="ok", confidence=1)

    result = asyncio.run(Agent.async_run.__wrapped__(agent))

    assert result.get_data("confidence") == 1.0
    assert result.get_data("sources") == []


def test_invalid_structured_output_is_rejected():
    agent = _agent(answer="unsafe", confidence=2)

    with pytest.raises(ValidationError):
        Agent.run.__wrapped__(agent)


def test_agents_without_output_model_keep_legacy_validation():
    class _LegacyAgent(_StructuredAgent):
        def output_model(self):
            return None

        def output_keys(self) -> list[str]:
            return ["answer"]

    result = Agent.run.__wrapped__(
        _agent(_LegacyAgent, answer="ok", untyped=object())
    )

    assert result.get_data("answer") == "ok"
    assert "untyped" in result.to_dict()


def test_output_model_hook_rejects_non_pydantic_classes():
    class _MisconfiguredAgent(_StructuredAgent):
        def output_model(self):
            return dict

    with pytest.raises(TypeError, match="Pydantic BaseModel subclass"):
        Agent.run.__wrapped__(
            _agent(_MisconfiguredAgent, answer="ok", confidence=1)
        )
