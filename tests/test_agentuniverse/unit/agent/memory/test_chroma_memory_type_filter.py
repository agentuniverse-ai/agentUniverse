import sys
import types
import unittest
from unittest.mock import patch


class _Collection:
    pass


class _FakeCollection:
    def __init__(self):
        self.where = None

    def get(self, where):
        self.where = where
        return {"ids": [], "metadatas": [], "documents": []}


def _install_chromadb_stub():
    chromadb_module = types.SimpleNamespace(Client=lambda settings: None)
    config_module = types.SimpleNamespace(Settings=lambda **kwargs: kwargs)
    collection_module = types.SimpleNamespace(Collection=_Collection)
    return patch.dict(
        sys.modules,
        {
            "chromadb": chromadb_module,
            "chromadb.config": config_module,
            "chromadb.api": types.SimpleNamespace(),
            "chromadb.api.models": types.SimpleNamespace(),
            "chromadb.api.models.Collection": collection_module,
        },
    )


class ChromaMemoryTypeFilterTest(unittest.TestCase):

    def test_get_accepts_tuple_type_filter(self):
        with _install_chromadb_stub():
            from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import ChromaMemoryStorage

        collection = _FakeCollection()
        storage = ChromaMemoryStorage()
        storage._collection = collection

        storage.get(type=("human", "ai"))

        self.assertEqual({"type": {"$in": ["human", "ai"]}}, collection.where)


if __name__ == "__main__":
    unittest.main()
