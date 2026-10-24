from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.memory.memory_storage.sql_alchemy_memory_storage import DefaultMemoryConverter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


def test_sql_memory_converter_preserves_database_id_for_unset_message_id():
    converter = DefaultMemoryConverter("message_round_trip")
    engine = create_engine("sqlite:///:memory:")
    converter.get_sql_model_class().__table__.create(engine)

    with sessionmaker(bind=engine)() as session:
        record = converter.to_sql_model(Message(content="generated"))
        session.add(record)
        session.commit()
        session.refresh(record)

        restored = converter.from_sql_model(record)

    assert record.id is not None
    assert restored.id == record.id
    assert restored.content == "generated"


def test_sql_memory_converter_preserves_explicit_message_id():
    converter = DefaultMemoryConverter("message_explicit_id")
    engine = create_engine("sqlite:///:memory:")
    converter.get_sql_model_class().__table__.create(engine)

    with sessionmaker(bind=engine)() as session:
        record = converter.to_sql_model(Message(id="message-42", content="explicit"))
        session.add(record)
        session.commit()
        session.refresh(record)

        restored = converter.from_sql_model(record)

    assert restored.id == "message-42"
    assert restored.content == "explicit"
