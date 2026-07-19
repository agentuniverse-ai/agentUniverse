#!/usr/bin/env python3
"""Chroma 1.x client construction and adapter compatibility tests."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

if importlib.util.find_spec("chromadb") is None:
    chromadb_stub = types.ModuleType("chromadb")
    chromadb_stub.QueryResult = dict
    api_stub = types.ModuleType("chromadb.api")
    models_stub = types.ModuleType("chromadb.api.models")
    collection_stub = types.ModuleType("chromadb.api.models.Collection")
    collection_stub.Collection = object
    sys.modules.update(
        {
            "chromadb": chromadb_stub,
            "chromadb.api": api_stub,
            "chromadb.api.models": models_stub,
            "chromadb.api.models.Collection": collection_stub,
        }
    )

from agentuniverse.agent.action.knowledge.store.chroma_client_factory import create_chroma_client
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.memory.conversation_memory.memory_storage.chroma_conversation_memory_storage import (
    ChromaConversationMemoryStorage,
)
from agentuniverse.agent.memory.memory_storage.chroma_memory_storage import ChromaMemoryStorage


class FakeSettings:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeChroma(types.ModuleType):
    def __init__(self):
        super().__init__("chromadb")
        self.calls = []

    def PersistentClient(self, **kwargs):
        self.calls.append(("persistent", kwargs))
        return "persistent-client"

    def HttpClient(self, **kwargs):
        self.calls.append(("http", kwargs))
        return "http-client"


class TestChromaClientFactory(unittest.TestCase):
    def call_with_fake(self, path, telemetry=False):
        chroma = FakeChroma()
        config = types.ModuleType("chromadb.config")
        config.Settings = FakeSettings
        with patch.dict(sys.modules, {"chromadb": chroma, "chromadb.config": config}):
            result = create_chroma_client(path, anonymized_telemetry=telemetry)
        return result, chroma.calls[0]

    def test_persistent_client_uses_public_constructor(self):
        result, call = self.call_with_fake("data/chroma", telemetry=True)
        self.assertEqual(result, "persistent-client")
        self.assertEqual(call[0], "persistent")
        self.assertEqual(call[1]["path"], "data/chroma")
        self.assertTrue(call[1]["settings"].kwargs["anonymized_telemetry"])

    def test_none_path_has_stable_local_default(self):
        _result, call = self.call_with_fake(None)
        self.assertEqual(call[1]["path"], "./chroma")

    def test_http_client_default_port(self):
        result, call = self.call_with_fake("http://chroma.internal")
        self.assertEqual(result, "http-client")
        self.assertEqual(call[1]["host"], "chroma.internal")
        self.assertEqual(call[1]["port"], 8000)
        self.assertFalse(call[1]["ssl"])

    def test_https_client_default_port_and_ssl(self):
        _result, call = self.call_with_fake("https://chroma.internal")
        self.assertEqual(call[1]["port"], 443)
        self.assertTrue(call[1]["ssl"])

    def test_explicit_server_port(self):
        _result, call = self.call_with_fake("http://localhost:9000")
        self.assertEqual(call[1]["port"], 9000)

    def test_rejects_server_url_path_query_and_unknown_scheme(self):
        for path in ("http://localhost:8000/api", "https://localhost/?x=1", "ftp://localhost/db"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.call_with_fake(path)

    def test_missing_dependency_has_install_hint(self):
        with patch.dict(sys.modules, {"chromadb": None}), self.assertRaisesRegex(ImportError, "pip install"):
            create_chroma_client("./chroma")


class TestChromaAdapters(unittest.TestCase):
    def test_chroma_store_delegates_client_creation(self):
        client = Mock()
        client.get_or_create_collection.return_value = Mock()
        store = ChromaStore(persist_path="./data")
        with patch(
            "agentuniverse.agent.action.knowledge.store.chroma_store.create_chroma_client",
            return_value=client,
        ) as factory:
            returned = store._new_client()
        factory.assert_called_once_with("./data")
        self.assertIs(returned, client)

    def test_empty_embeddings_are_omitted_on_upsert_and_update(self):
        collection = Mock()
        store = ChromaStore(collection=collection)
        document = Document(id="1", text="hello", embedding=[])
        store.upsert_document([document])
        store.update_document([document])
        self.assertIsNone(collection.upsert.call_args.kwargs["embeddings"])
        self.assertIsNone(collection.update.call_args.kwargs["embeddings"])

    def test_memory_storages_use_shared_factory(self):
        for module, storage_class in (
            (
                "agentuniverse.agent.memory.memory_storage.chroma_memory_storage",
                ChromaMemoryStorage,
            ),
            (
                "agentuniverse.agent.memory.conversation_memory.memory_storage.chroma_conversation_memory_storage",
                ChromaConversationMemoryStorage,
            ),
        ):
            client = Mock()
            client.get_or_create_collection.return_value = Mock()
            storage = storage_class(persist_path="https://chroma.example")
            with patch(f"{module}.create_chroma_client", return_value=client) as factory:
                returned = storage._init_collection()
            factory.assert_called_once_with("https://chroma.example")
            self.assertIs(returned, client)


class TestCompatibilityMetadata(unittest.TestCase):
    def test_python312_numpy2_and_chroma1_constraints(self):
        project_file = next(
            parent / "pyproject.toml" for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file()
        )
        with project_file.open("rb") as stream:
            project = tomllib.load(stream)["tool"]["poetry"]
        self.assertIn("Programming Language :: Python :: 3.12", project["classifiers"])
        dependencies = project["dependencies"]
        self.assertEqual(dependencies["numpy"], ">=1.26.0,<3.0.0")
        self.assertEqual(dependencies["chromadb"], "^1.5.9")


if __name__ == "__main__":
    unittest.main()
