from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.message import Message


def test_conversation_conversion_handles_mixed_message_subclasses():
    existing = ConversationMessage(content="first", type="input")
    plain = Message(content="second", type="output", source="agent")

    result = ConversationMessage.check_and_convert_message(
        [existing, plain], session_id="session"
    )

    assert result[0] is existing
    assert isinstance(result[1], ConversationMessage)
    assert result[1].content == "second"
    assert result[1].conversation_id == "session"
