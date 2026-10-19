"""Exercise SQLiteStore operations on one real connection shared by threads."""
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from contextlib import closing
import sqlite3
from threading import Event

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


@pytest.fixture
def store(tmp_path):
    instance = SQLiteStore(db_path=str(tmp_path / "store.db"))
    instance._new_client()
    yield instance
    instance.conn.close()


def rows(store):
    with closing(sqlite3.connect(store.db_path)) as observer:
        return observer.execute("SELECT id FROM documents ORDER BY id").fetchall()


def schedule_blocked(pool, operation):
    started = Event()

    def run():
        started.set()
        return operation()

    future = pool.submit(run)
    assert started.wait(5)
    try:
        future.result(timeout=0.3)
    except TimeoutError:
        pass
    return future


@pytest.mark.parametrize("writer", ["insert_document", "upsert_document"])
@pytest.mark.parametrize("other", ["query", "insert_document", "upsert_document", "delete_document"])
def test_other_operation_cannot_commit_a_failed_write(store, monkeypatch, writer, other):
    paused, release = Event(), Event()

    def extract(self, document):
        if document.id == "failed":
            paused.set()
            assert release.wait(5)
            raise ValueError("keyword processor failed")
        document.keywords = {document.text}

    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", extract)
    store.insert_document([Document(id="victim", text="victim")])

    def competing_operation():
        if other == "query":
            return store.query(Query(query_str="absent", keywords={"absent"}))
        if other == "delete_document":
            return store.delete_document("victim")
        return getattr(store, other)([Document(id="kept", text="kept")])

    with ThreadPoolExecutor(max_workers=2) as pool:
        failed = pool.submit(getattr(store, writer), [Document(id="failed", text="alpha")])
        try:
            assert paused.wait(5)
            competing = schedule_blocked(pool, competing_operation)
            visible_while_paused = rows(store)
        finally:
            release.set()
        with pytest.raises(ValueError, match="keyword processor failed"):
            failed.result(timeout=5)
        competing.result(timeout=5)

    expected = [] if other == "delete_document" else [("victim",)]
    if other in ("insert_document", "upsert_document"):
        expected = [("kept",), ("victim",)]
    assert ("failed",) not in visible_while_paused
    assert rows(store) == expected


@pytest.mark.parametrize("writer", ["insert_document", "upsert_document"])
def test_query_sees_a_complete_successful_batch(store, monkeypatch, writer):
    paused, release = Event(), Event()

    def extract(self, document):
        if document.id == "first":
            paused.set()
            assert release.wait(5)
        document.keywords = {document.text}

    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", extract)
    documents = [Document(id="first", text="alpha"), Document(id="second", text="beta")]
    with ThreadPoolExecutor(max_workers=2) as pool:
        writing = pool.submit(getattr(store, writer), documents)
        try:
            assert paused.wait(5)
            reading = schedule_blocked(pool, lambda: store.query(
                Query(query_str="alpha beta", keywords={"alpha", "beta"})))
        finally:
            release.set()
        writing.result(timeout=5)
        result = reading.result(timeout=5)
    assert {document.id for document in result} == {"first", "second"}


def test_delete_cannot_remove_a_document_halfway_through_query(store, monkeypatch):
    paused, release = Event(), Event()

    def extract(self, document):
        document.keywords = {"alpha"}

    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", extract)
    store.insert_document([Document(id="retained", text="alpha", metadata={"version": 1})])
    original = SQLiteStore.compute_bm25

    def score(self, *args, **kwargs):
        paused.set()
        assert release.wait(5)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SQLiteStore, "compute_bm25", score)
    with ThreadPoolExecutor(max_workers=2) as pool:
        reading = pool.submit(store.query, Query(query_str="alpha", keywords={"alpha"}))
        try:
            assert paused.wait(5)
            deleting = schedule_blocked(pool, lambda: store.delete_document("retained"))
        finally:
            release.set()
        result = reading.result(timeout=5)
        deleting.result(timeout=5)
    assert [(document.id, document.text, document.metadata) for document in result] == [
        ("retained", "alpha", {"version": 1})]
    assert rows(store) == []


def test_unrelated_store_instances_do_not_block_each_other(store, tmp_path, monkeypatch):
    paused, release = Event(), Event()
    other = SQLiteStore(db_path=str(tmp_path / "other.db"))
    other._new_client()

    def extract(self, document):
        if self is store:
            paused.set()
            assert release.wait(5)
        document.keywords = {document.text}

    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", extract)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            writing = pool.submit(store.insert_document, [Document(id="first", text="alpha")])
            try:
                assert paused.wait(5)
                second = pool.submit(other.insert_document, [Document(id="second", text="beta")])
                second.result(timeout=2)
                assert rows(other) == [("second",)]
            finally:
                release.set()
            writing.result(timeout=5)
    finally:
        other.conn.close()


@pytest.mark.parametrize("writer", ["insert_document", "upsert_document"])
def test_failed_operation_does_not_block_later_use(store, monkeypatch, writer):
    def extract(self, document):
        if document.id == "failed":
            raise ValueError("keyword processor failed")
        document.keywords = {"alpha"}

    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", extract)
    with ThreadPoolExecutor(max_workers=1) as pool:
        failed = pool.submit(getattr(store, writer), [Document(id="failed", text="alpha")])
        with pytest.raises(ValueError, match="keyword processor failed"):
            failed.result(timeout=5)
        pool.submit(store.insert_document, [Document(id="kept", text="alpha")]).result(timeout=5)
        result = pool.submit(store.query, Query(query_str="alpha", keywords={"alpha"})).result(timeout=5)
    assert [document.id for document in result] == ["kept"]
    assert rows(store) == [("kept",)]


@pytest.mark.parametrize("writer", ["insert_document", "upsert_document"])
def test_keyword_processor_read_does_not_commit_its_callers_write(store, monkeypatch, writer):
    def extract(self, document):
        assert self.query(Query(query_str="absent", keywords={"absent"})) == []
        raise ValueError("keyword processor failed")

    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", extract)
    with pytest.raises(ValueError, match="keyword processor failed"):
        getattr(store, writer)([Document(id="failed", text="alpha")])
    assert rows(store) == []

