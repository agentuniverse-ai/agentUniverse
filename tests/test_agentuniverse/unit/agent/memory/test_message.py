import pytest
from langchain_core.prompts import (
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from agentuniverse.agent.memory.message import Message


@pytest.mark.parametrize(
    ("message_type", "expected_type"),
    [
        ("system", SystemMessagePromptTemplate),
        ("human", HumanMessagePromptTemplate),
        ("user", HumanMessagePromptTemplate),
        ("input", HumanMessagePromptTemplate),
        ("ai", AIMessagePromptTemplate),
        ("assistant", AIMessagePromptTemplate),
        ("output", AIMessagePromptTemplate),
    ],
)
def test_as_langchain_supports_declared_message_roles(message_type, expected_type):
    converted = Message(type=message_type, content="hello").as_langchain()

    assert isinstance(converted, expected_type)


def test_as_langchain_rejects_unknown_message_role():
    with pytest.raises(ValueError, match="Unsupported message type: tool"):
        Message(type="tool", content="hello").as_langchain()
