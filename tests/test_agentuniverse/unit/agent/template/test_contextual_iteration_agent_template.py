import asyncio
import json
from typing import ClassVar

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.contextual_iteration_agent_template import (
    ContextualIterationAgentTemplate,
)


class _FakePrompt:
    input_variables: ClassVar[list[str]] = ["chat_history"]

    def as_langchain(self):
        return self

    def format(self, **kwargs):
        return kwargs.get("chat_history", "")

    def __or__(self, other):
        return self


class _FakeLLM:
    def as_langchain_runnable(self, params):
        return object()


def _make_agent():
    agent = ContextualIterationAgentTemplate()
    agent.agent_model = AgentModel(
        info={"name": "contextual"},
        profile={"llm_model": {"name": "fake"}},
        memory={},
        action={},
    )
    agent.iteration = 2
    agent.continue_prompt_version = "continue"
    agent.if_loop_prompt_version = None
    return agent


def _configure_dependencies(monkeypatch):
    prompt = _FakePrompt()
    module = (
        "agentuniverse.agent.template.contextual_iteration_agent_template"
    )
    monkeypatch.setattr(f"{module}.assemble_memory_input", lambda *args, **kwargs: None)
    monkeypatch.setattr(f"{module}.assemble_memory_output", lambda *args, **kwargs: None)
    monkeypatch.setattr(f"{module}.process_llm_token", lambda *args, **kwargs: None)
    monkeypatch.setattr(f"{module}.StrOutputParser", lambda: object())
    monkeypatch.setattr(Agent, "process_prompt", lambda *args, **kwargs: prompt)
    return prompt


def test_sync_iterations_include_previous_continuation_in_history(monkeypatch):
    prompt = _configure_dependencies(monkeypatch)
    agent = _make_agent()
    observed_histories = []
    responses = iter(["initial", "continue-1", "continue-2"])

    def invoke_chain(self, chain, agent_input, input_object, **kwargs):
        observed_histories.append(agent_input.get("chat_history"))
        return next(responses)

    monkeypatch.setattr(ContextualIterationAgentTemplate, "invoke_chain", invoke_chain)

    result = agent.customized_execute(
        InputObject({}), {"input": "question"}, None, _FakeLLM(), prompt
    )

    assert result["output"] == "initial\ncontinue-1\ncontinue-2"
    assert len(json.loads(observed_histories[2])) == 2
    assert json.loads(observed_histories[2])[-1]["assistant"] == "continue-1"


def test_loop_decision_sees_latest_continuation(monkeypatch):
    prompt = _configure_dependencies(monkeypatch)
    agent = _make_agent()
    agent.if_loop_prompt_version = "judge"
    observed_histories = []
    responses = iter(["initial", "continue-1", "no"])

    def invoke_chain(self, chain, agent_input, input_object, **kwargs):
        observed_histories.append(agent_input.get("chat_history"))
        return next(responses)

    monkeypatch.setattr(ContextualIterationAgentTemplate, "invoke_chain", invoke_chain)

    result = agent.customized_execute(
        InputObject({}), {"input": "question"}, None, _FakeLLM(), prompt
    )

    assert result["output"] == "initial\ncontinue-1"
    decision_history = json.loads(observed_histories[2])
    assert decision_history[-1]["assistant"] == "continue-1"


def test_async_iterations_include_previous_continuation_in_history(monkeypatch):
    prompt = _configure_dependencies(monkeypatch)
    agent = _make_agent()
    observed_histories = []
    responses = iter(["initial", "continue-1", "continue-2"])

    async def invoke_chain(self, chain, agent_input, input_object, **kwargs):
        observed_histories.append(agent_input.get("chat_history"))
        return next(responses)

    monkeypatch.setattr(
        ContextualIterationAgentTemplate, "async_invoke_chain", invoke_chain
    )

    result = asyncio.run(
        agent.customized_async_execute(
            InputObject({}), {"input": "question"}, None, _FakeLLM(), prompt
        )
    )

    assert result["output"] == "initial\ncontinue-1\ncontinue-2"
    assert len(json.loads(observed_histories[2])) == 2
    assert json.loads(observed_histories[2])[-1]["assistant"] == "continue-1"
