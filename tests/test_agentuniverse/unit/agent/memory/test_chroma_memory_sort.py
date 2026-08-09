import sys
import types
import unittest
from unittest.mock import patch


class _Collection:
    pass


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


class ChromaMemorySortTest(unittest.TestCase):

    def test_to_messages_sorts_when_metadata_is_none(self):
        with _install_chromadb_stub():
            from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import ChromaMemoryStorage

        storage = ChromaMemoryStorage()
        result = {
            "ids": ["1", "2"],
            "documents": ["without metadata", "with metadata"],
            "metadatas": [None, {"gmt_created": "2026-01-01T00:00:00"}],
        }

        messages = storage.to_messages(result, sort_by_time=True)

        self.assertEqual(["1", "2"], [message.id for message in messages])


if __name__ == "__main__":
    unittest.main()
