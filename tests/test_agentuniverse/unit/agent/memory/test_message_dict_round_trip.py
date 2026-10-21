from agentuniverse.agent.memory.message import Message


def test_message_dict_round_trip_preserves_id_and_payload():
    message = Message(
        id="message-42",
        type="human",
        content="hello",
        metadata={"trace": "abc"},
        source="user",
    )

    restored = Message.from_dict(message.to_dict())

    assert restored == message
