from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage


def test_conversation_messages_get_unique_default_ids():
    first = ConversationMessage()
    second = ConversationMessage()

    assert first.id
    assert second.id
    assert first.id != second.id
