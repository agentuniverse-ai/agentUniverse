"""Placeholder extraction follows f-string rules instead of a single-brace regex."""

import pytest

from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt, iter_placeholders
from agentuniverse.prompt.prompt_model import AgentPromptModel


@pytest.mark.parametrize(
    "template,expected",
    [
        ("Hello {name}", ["name"]),
        ("Use {{literal}} braces", []),
        ("Use {{literal}} braces and {real}", ["real"]),
        ("Score {score:>10} for {name}", ["score", "name"]),
        ("repr {value!r}", ["value"]),
        ("empty {} stays literal", []),
        ("{a}{b}", ["a", "b"]),
        ("no placeholders at all", []),
    ],
)
def test_iter_placeholders_returns_only_real_fields(template, expected):
    """Escaped braces, format specs, conversions and empty pairs are not fields."""
    assert iter_placeholders(template) == expected


def test_iter_placeholders_does_not_return_a_truncated_name():
    """`{{topic}}` must not turn into the variable name `{topic`."""
    assert iter_placeholders("Describe {{topic}}.") == []
    assert "{topic" not in iter_placeholders("Describe {{topic}}.")


def test_prompt_build_prompt_uses_the_same_extraction():
    """`Prompt.build_prompt` must not require the caller to fill a literal brace pair."""
    model = AgentPromptModel(
        instruction="Answer in JSON after reading {{sample}}, then answer {question}."
    )
    prompt = Prompt().build_prompt(model, ["instruction"])

    assert prompt.input_variables == ["question"]
    assert prompt.prompt_template == (
        "Answer in JSON after reading {{sample}}, then answer {question}."
    )


def test_chat_prompt_keeps_field_order_across_messages():
    """Each message contributes its own fields in declaration order."""
    prompt = ChatPrompt()
    prompt.messages = [
        Message(type="system", content="You are a {role}. Show {{example}} if needed."),
        Message(type="human", content="{question}"),
    ]

    assert prompt.extract_placeholders() == ["role", "question"]
