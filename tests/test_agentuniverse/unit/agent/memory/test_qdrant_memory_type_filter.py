from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import QdrantMemoryStorage


def test_qdrant_type_filter_keeps_scalar_string_intact():
    result = QdrantMemoryStorage._build_filter(
        session_id=None, agent_id=None, source=None, type_value="human"
    )

    assert result.must[0].match.value == "human"


def test_qdrant_type_filter_supports_multiple_values():
    result = QdrantMemoryStorage._build_filter(
        session_id=None, agent_id=None, source=None, type_value=["human", "ai"]
    )

    assert result.must[0].match.any == ["human", "ai"]
