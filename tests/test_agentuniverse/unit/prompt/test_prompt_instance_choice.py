"""Prompt manager copy requests isolate mutable prompt state without changing defaults."""
import pytest

from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt_manager import PromptManager


@pytest.fixture
def registered_prompt(monkeypatch):
    manager = PromptManager()
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    prompt = ChatPrompt(
        prompt_version="test.prompt.v1", input_variables=["question"],
        messages=[Message(type="human", content="{question}", metadata={"tags": ["original"]})],
    )
    manager.register(prompt.get_instance_code(), prompt)
    return manager, prompt


@pytest.mark.parametrize("kwargs", [{}, {"new_instance": False}])
def test_default_and_explicit_false_keep_registered_identity(registered_prompt, kwargs):
    manager, prompt = registered_prompt
    assert manager.get_instance_obj("test.prompt.v1", **kwargs) is prompt


def test_explicit_copy_isolates_nested_prompt_state(registered_prompt):
    manager, prompt = registered_prompt
    first = manager.get_instance_obj("test.prompt.v1", new_instance=True)
    second = manager.get_instance_obj("test.prompt.v1", new_instance=True)
    assert first is not prompt and second is not first
    first.messages[0].metadata["tags"].append("changed")
    first.messages[0].content = "changed"
    first.input_variables.append("extra")
    assert prompt.messages[0].content == second.messages[0].content == "{question}"
    assert prompt.messages[0].metadata == second.messages[0].metadata == {"tags": ["original"]}
    assert prompt.input_variables == second.input_variables == ["question"]
    assert second.as_langchain().format_messages(question="hello")[0].content == "hello"


@pytest.mark.parametrize("copy", [False, True])
def test_unknown_prompt_remains_none(registered_prompt, copy):
    manager, _ = registered_prompt
    assert manager.get_instance_obj("missing", new_instance=copy) is None
