"""ChromaStore should identify an unregistered ``embedding_model``.

The store configuration names an ``EMBEDDING`` component.  Before this test,
resolving a name that was not registered returned ``None`` and the failure
surfaced later as ``'NoneType' object has no attribute 'get_embeddings'``.
The failure remains an ``AttributeError`` for compatibility, but now names the
store, the configured field, the missing component and the store config path.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import agentuniverse.base.component.component_manager_base as component_manager_base
from agentuniverse.agent.action.knowledge.embedding.embedding_manager import (
    EmbeddingManager,
)
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query

APP_NAME = "chroma_embedding_error_test"


@pytest.fixture
def isolated_embedding_registry(monkeypatch):
    """Use an empty embedding registry and a deterministic application name."""
    monkeypatch.setattr(
        component_manager_base,
        "ApplicationConfigManager",
        lambda: SimpleNamespace(
            app_configer=SimpleNamespace(base_info_appname=APP_NAME)
        ),
    )
    monkeypatch.setattr(EmbeddingManager(), "_instance_obj_map", {})


def _store(embedding_model, collection, config_path):
    return ChromaStore(
        name="civil_law_chroma_store",
        description="civil law vectors",
        component_config_path=str(config_path),
        embedding_model=embedding_model,
        collection=collection,
    )


@pytest.mark.parametrize(
    "operation",
    ["query", "insert_document", "upsert_document", "update_document"],
)
def test_unregistered_embedding_model_reports_store_context(
    isolated_embedding_registry, operation, tmp_path
):
    collection = MagicMock()
    config_path = tmp_path / "civil_law_chroma_store.yaml"
    store = _store("missing_embedding", collection, config_path)

    with pytest.raises(AttributeError) as caught:
        if operation == "query":
            store.query(Query(query_str="civil code"))
        else:
            getattr(store, operation)([Document(id="doc-1", text="civil code")])

    message = str(caught.value)
    for context in (
        "ChromaStore",
        "civil_law_chroma_store",
        "embedding_model",
        "missing_embedding",
        "EMBEDDING",
        str(config_path),
    ):
        assert context in message
    assert "NoneType" not in message
    collection.query.assert_not_called()
    collection.add.assert_not_called()
    collection.upsert.assert_not_called()
    collection.update.assert_not_called()


def test_registered_embedding_model_still_queries(
    isolated_embedding_registry, tmp_path
):
    embedding = MagicMock()
    embedding.get_embeddings.return_value = [[0.25, 0.75]]
    embedding.create_copy.return_value = embedding
    EmbeddingManager()._instance_obj_map[
        f"{APP_NAME}.embedding.available_embedding"
    ] = embedding

    collection = MagicMock()
    collection.query.return_value = {
        "ids": [["doc-1"]],
        "documents": [["civil code"]],
        "embeddings": [[[0.25, 0.75]]],
        "metadatas": [[{"source": "test"}]],
    }
    store = _store(
        "available_embedding", collection, tmp_path / "civil_law_chroma_store.yaml"
    )

    documents = store.query(Query(query_str="civil code", similarity_top_k=3))

    embedding.get_embeddings.assert_called_once_with(
        ["civil code"], text_type="query"
    )
    collection.query.assert_called_once_with(
        n_results=3, query_embeddings=[0.25, 0.75]
    )
    assert [document.id for document in documents] == ["doc-1"]
    assert [document.text for document in documents] == ["civil code"]


def test_store_without_embedding_model_keeps_default_chroma_path(
    isolated_embedding_registry, tmp_path
):
    collection = MagicMock()
    collection.query.return_value = {
        "ids": [["doc-1"]],
        "documents": [["civil code"]],
        "embeddings": None,
        "metadatas": None,
    }
    store = _store(None, collection, tmp_path / "civil_law_chroma_store.yaml")

    documents = store.query(Query(query_str="civil code"))

    collection.query.assert_called_once_with(
        n_results=10, query_texts=["civil code"]
    )
    assert [document.id for document in documents] == ["doc-1"]
