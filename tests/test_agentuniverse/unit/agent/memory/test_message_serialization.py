from agentuniverse.agent.memory.message import Message


def test_message_to_dict_preserves_id_for_round_trip():
    message = Message(
        id="message-42",
        type="human",
        content="hello",
        metadata={"source": "test"},
        source="user",
    )

    restored = Message.from_dict(message.to_dict())

    assert restored == message
