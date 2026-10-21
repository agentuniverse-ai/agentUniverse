import sys
import types

import pytest

# Chroma is an optional runtime dependency. These minimal modules let the
# validation tests exercise filter construction without a database client.
if "chromadb" not in sys.modules:
    chromadb = types.ModuleType("chromadb")
    chromadb_config = types.ModuleType("chromadb.config")
    chromadb_config.Settings = object
    chromadb_api = types.ModuleType("chromadb.api")
    chromadb_models = types.ModuleType("chromadb.api.models")
    chromadb_collection = types.ModuleType("chromadb.api.models.Collection")
    chromadb_collection.Collection = object
    chromadb.config = chromadb_config
    sys.modules.update(
        {
            "chromadb": chromadb,
            "chromadb.config": chromadb_config,
            "chromadb.api": chromadb_api,
            "chromadb.api.models": chromadb_models,
            "chromadb.api.models.Collection": chromadb_collection,
        }
    )

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
