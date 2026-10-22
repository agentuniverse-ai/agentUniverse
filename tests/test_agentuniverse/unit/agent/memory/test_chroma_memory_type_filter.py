import pytest

# Chroma is an optional runtime dependency. Use the installed package when
# available and skip these integration-bound tests otherwise; do not inject
# incomplete modules into global sys.modules during test collection.
pytest.importorskip("chromadb")

from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import ChromaMemoryStorage


class FakeCollection:
    def __init__(self):
        self.last_where = None

    def get(self, where):
        self.last_where = where
        return {"ids": []}


def test_chroma_memory_rejects_unsupported_type_filter():
    storage = ChromaMemoryStorage()
    storage._collection = FakeCollection()

    with pytest.raises(TypeError, match="string or list"):
        storage.get(type=42)


def test_chroma_memory_keeps_string_type_filter_shape():
    storage = ChromaMemoryStorage()
    collection = FakeCollection()
    storage._collection = collection

    assert storage.get(type="human") == []
    assert collection.last_where == {"type": {"$in": ["human"]}}
