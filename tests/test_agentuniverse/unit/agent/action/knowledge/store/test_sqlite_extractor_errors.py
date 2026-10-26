"""SQLite extractor configuration failures should identify the invalid setting."""

import sqlite3
from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager


class KeywordExtractor(DocProcessor):
    def _process_docs(self, origin_docs, query=None):
        for document in origin_docs:
            document.keywords = {"alpha"}
        return origin_docs


@pytest.fixture
def store(monkeypatch):
    monkeypatch.setattr(
        ApplicationConfigManager(),
        "_ApplicationConfigManager__app_configer",
        SimpleNamespace(base_info_appname="extractor_error_test"),
    )
    monkeypatch.setattr(DocProcessorManager(), "_instance_obj_map", {})
    connection = sqlite3.connect(":memory:")
    instance = SQLiteStore(
        name="article_store", keyword_extractor="missing_extractor", conn=connection
    )
    instance._create_tables()
    yield instance
    connection.close()


@pytest.mark.parametrize("operation", ["query", "insert_document", "upsert_document"])
def test_unknown_extractor_reports_configuration_and_preserves_data(store, operation):
    with store.conn:
        store.conn.execute(
            "INSERT INTO documents (id, text, word_count, metadata) VALUES (?, ?, ?, ?)",
            ("existing", "alpha", 1, None),
        )
        store.conn.execute(
            "INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)",
            ("alpha", "existing"),
        )

    with pytest.raises(ValueError) as caught:
        if operation == "query":
            store.query(Query(query_str="alpha"))
        else:
            getattr(store, operation)([Document(id="existing", text="replacement")])

    message = str(caught.value)
    for context in ("article_store", "keyword_extractor", "missing_extractor", "DOC_PROCESSOR"):
        assert context in message
    assert "configuration" in message
    assert store.conn.execute("SELECT id, text FROM documents").fetchall() == [
        ("existing", "alpha")
    ]
    assert store.conn.execute("SELECT term, doc_id FROM inverted_index").fetchall() == [
        ("alpha", "existing")
    ]


def test_registered_extractor_still_supports_indexing_and_query(store):
    extractor = KeywordExtractor(name="available_extractor")
    DocProcessorManager().register(extractor.get_instance_code(), extractor)
    store.keyword_extractor = extractor.name

    store.insert_document([Document(id="article", text="alpha")])
    results = store.query(Query(query_str="alpha"))

    assert [document.id for document in results] == ["article"]


def test_explicit_query_keywords_do_not_require_an_extractor(store):
    assert store.query(Query(keywords={"alpha"})) == []


def test_unconfigured_extractor_raises_value_error(store):
    store.keyword_extractor = None
    with pytest.raises(ValueError, match="specify a keyword extractor"):
        store.query(Query(query_str="alpha"))
