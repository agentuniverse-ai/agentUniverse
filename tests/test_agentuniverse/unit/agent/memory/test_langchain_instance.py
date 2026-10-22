import pytest

from agentuniverse.agent.memory.langchain_instance import (
    AuConversationSummaryBufferMemory,
    AuConversationTokenBufferMemory,
)
from agentuniverse.agent.memory.message import Message
from agentuniverse.llm.default.default_openai_llm import DefaultOpenAILLM


@pytest.fixture
def langchain_llm():
    return DefaultOpenAILLM(model_name="gpt-4o").as_langchain()


@pytest.mark.parametrize(
    "memory_class",
    [AuConversationSummaryBufferMemory, AuConversationTokenBufferMemory],
)
def test_build_memory_ignores_unpaired_trailing_message(memory_class, langchain_llm):
    messages = [Message(type="human", content="unanswered question")]

    memory = memory_class(llm=langchain_llm, messages=messages)

    assert memory.chat_memory.messages == []
    assert messages == [Message(type="human", content="unanswered question")]
