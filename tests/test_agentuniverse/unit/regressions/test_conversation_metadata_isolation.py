from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.message import Message


def test_conversation_conversion_does_not_mutate_source_metadata():
    source_metadata = {"custom": "value", "session_id": "stored-session"}
    message = Message(
        content="summary", type="summarize", source="agent", metadata=source_metadata
    )

    converted = ConversationMessage.from_message(message, session_id=None)

    assert message.metadata == {"custom": "value", "session_id": "stored-session"}
    assert converted.metadata is not message.metadata
    assert converted.metadata["prefix"] == "之前对话的摘要："
    assert converted.conversation_id == "stored-session"
