from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import (
    ChromaMemoryStorage,
)


class StubCollection:
    def get(self, **kwargs):
        return {
            "ids": ["m3", "m1", "m4", "m2"],
            "documents": ["three", "one", "four", "two"],
            "metadatas": [
                {"gmt_created": "2026-01-01T00:00:03"},
                {"gmt_created": "2026-01-01T00:00:01"},
                {"gmt_created": "2026-01-01T00:00:04"},
                {"gmt_created": "2026-01-01T00:00:02"},
            ],
        }


def test_get_returns_the_most_recent_messages_in_chronological_order():
    storage = ChromaMemoryStorage()
    storage._collection = StubCollection()

    messages = storage.get(top_k=2)

    assert [message.id for message in messages] == ["m3", "m4"]
