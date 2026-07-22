import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class _Collection:
    pass


class _FakeCollection:
    def __init__(self):
        self.metadatas = []

    def add(self, ids, documents, metadatas, embeddings):
        self.metadatas.append(dict(metadatas[0]))


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


class ChromaMemoryStorageTest(unittest.TestCase):

    def test_add_uses_independent_metadata_per_message(self):
        with _install_chromadb_stub():
            from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import ChromaMemoryStorage

        collection = _FakeCollection()
        storage = ChromaMemoryStorage()
        storage._collection = collection

        first = SimpleNamespace(id="1", content="first", source="doc-a", type="human")
        second = SimpleNamespace(id="2", content="second", source=None, type=None)

        storage.add([first, second], session_id="session", agent_id="agent")

        self.assertEqual("doc-a", collection.metadatas[0]["source"])
        self.assertEqual("human", collection.metadatas[0]["type"])
        self.assertNotIn("source", collection.metadatas[1])
        self.assertEqual("", collection.metadatas[1]["type"])


if __name__ == "__main__":
    unittest.main()
