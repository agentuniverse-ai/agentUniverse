"""Durable source ownership, revision conflicts and real SQLite rollback."""
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.agent.action.knowledge.store.sqlite_source_sync import (
    SQLiteSourceSynchronizer, SourceIndexDrift, SourceRevisionConflict,
)


@pytest.fixture
def store(tmp_path, monkeypatch):
    instance = SQLiteStore(db_path=str(tmp_path / "sync.db"))
    instance._new_client()
    # Return keywords without mutating the document: the return contract matters.
    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", lambda self, document: set(document.text.split()))
    try:
        yield instance
    finally:
        instance.conn.close()


def doc(identity="a", text="alpha", **metadata):
    return Document(id=identity, text=text, metadata=metadata or None)


def sync(store, documents, revision=0, source="source-A", **kwargs):
    return SQLiteSourceSynchronizer(store).sync(source, documents, expected_revision=revision,
                                                pipeline_revision="fixture-v1", **kwargs)


def snapshot(store):
    return {name: store.conn.execute("SELECT * FROM " + name + " ORDER BY 1").fetchall()
            for name in ("documents", "inverted_index", "au_source_state_v1", "au_source_members_v1")}


def test_insert_noop_update_delete_and_reopen(store):
    first = sync(store, [doc(), doc("b", "beta")])
    assert first["inserted"] == 2 and first["revision"] == 1
    assert store.query(Query(query_str="alpha", keywords={"alpha"}))[0].id == first["document_ids"]["a"]
    before = snapshot(store)
    repeated = sync(store, [doc(), doc("b", "beta")], revision=1)
    assert repeated["revision"] == 1 and repeated["unchanged"] == 2
    assert snapshot(store) == before
    second = sync(store, [doc("a", "gamma"), doc("c", "delta")], revision=1)
    assert (second["inserted"], second["updated"], second["deleted"], second["revision"]) == (1, 1, 1, 2)
    assert second["document_ids"]["a"] == first["document_ids"]["a"]
    assert store.query(Query(query_str="alpha", keywords={"alpha"})) == []
    assert store.query(Query(query_str="beta", keywords={"beta"})) == []
    store.conn.close()
    store._new_client()
    assert SQLiteSourceSynchronizer(store).inspect_source("source-A") == {
        "source": "source-A", "revision": 2, "document_count": 2, "drift_ids": []}
    assert store.query(Query(query_str="gamma", keywords={"gamma"}))[0].text == "gamma"


def test_source_and_unmanaged_rows_are_not_deleted(store):
    first = sync(store, [doc()])
    second = sync(store, [doc()], source="source-B")
    assert first["document_ids"] != second["document_ids"]
    with store.conn:
        store.conn.execute("INSERT INTO documents VALUES ('manual','unmanaged',1,'{}')")
    with pytest.raises(ValueError, match="allow_empty"):
        sync(store, [], revision=1)
    removed = sync(store, [], revision=1, allow_empty=True)
    assert removed["deleted"] == 1
    assert {row[0] for row in store.conn.execute("SELECT id FROM documents")} == {"manual", second["document_ids"]["a"]}
    assert sync(store, [], revision=2, allow_empty=True)["revision"] == 2


def test_stale_revision_has_no_changes(store):
    sync(store, [doc()])
    before = snapshot(store)
    with pytest.raises(SourceRevisionConflict):
        sync(store, [doc(text="stale")], revision=0)
    assert snapshot(store) == before


def test_failed_mid_transaction_restores_rows_terms_and_manifest(store):
    sync(store, [doc(), doc("b", "beta")])
    before = snapshot(store)
    with store.conn:
        store.conn.execute("""CREATE TRIGGER reject_payload BEFORE INSERT ON documents
            WHEN NEW.text='reject' BEGIN SELECT RAISE(ABORT, 'fixture rejection'); END""")
    with pytest.raises(sqlite3.IntegrityError, match="fixture rejection"):
        sync(store, [doc("a", "reject"), doc("c", "gamma")], revision=1)
    assert snapshot(store) == before
    assert sync(store, [doc("a", "accepted")], revision=1)["revision"] == 2


@pytest.mark.parametrize("sql", [
    "UPDATE documents SET text='changed' WHERE id=?",
    "DELETE FROM documents WHERE id=?",
    "DELETE FROM inverted_index WHERE doc_id=?",
    "INSERT INTO inverted_index(term,doc_id) VALUES ('extra',?)",
    "INSERT INTO inverted_index(term,doc_id) VALUES ('alpha',?)",
])
def test_external_drift_is_reported_and_never_silently_repaired(store, sql):
    identity = sync(store, [doc()])["document_ids"]["a"]
    with store.conn:
        store.conn.execute(sql, (identity,))
    before = snapshot(store)
    assert SQLiteSourceSynchronizer(store).inspect_source("source-A")["drift_ids"] == [identity]
    with pytest.raises(SourceIndexDrift):
        sync(store, [], revision=1, allow_empty=True)
    assert snapshot(store) == before


def test_unmanaged_id_collision_is_not_adopted(store):
    identity = sync(store, [doc()])["document_ids"]["a"]
    sync(store, [], revision=1, allow_empty=True)
    with store.conn:
        store.conn.execute("INSERT INTO documents VALUES (?, 'foreign',1,'{}')", (identity,))
    with pytest.raises(SourceIndexDrift, match="collides"):
        sync(store, [doc()], revision=2)
    assert store.conn.execute("SELECT text FROM documents WHERE id=?", (identity,)).fetchone() == ("foreign",)


def test_final_revision_write_failure_restores_entire_snapshot(store):
    sync(store, [doc(), doc("b", "beta")])
    before = snapshot(store)
    with store.conn:
        store.conn.execute("""CREATE TRIGGER reject_revision BEFORE INSERT ON au_source_state_v1
            WHEN NEW.revision=2 BEGIN SELECT RAISE(ABORT, 'revision rejected'); END""")
    # Fail only after new/changed rows, deleted rows, terms and membership have
    # already been processed, rather than at an early content insertion.
    with pytest.raises(sqlite3.IntegrityError, match="revision rejected"):
        sync(store, [doc("a", "changed"), doc("c", "new")], revision=1)
    assert snapshot(store) == before
    assert SQLiteSourceSynchronizer(store).inspect_source("source-A")["drift_ids"] == []
    with store.conn:
        store.conn.execute("DROP TRIGGER reject_revision")
    assert sync(store, [doc("a", "changed"), doc("c", "new")], revision=1)["revision"] == 2


def test_keyword_failure_before_write_and_input_isolation(store, monkeypatch):
    sync(store, [doc()])
    before = snapshot(store)
    original = doc(text="beta", nested={"items": [1]})
    def fail(self, detached):
        detached.metadata["nested"]["items"].append(2)
        raise RuntimeError("extractor failed")
    monkeypatch.setattr(SQLiteStore, "_get_document_keyword", fail)
    with pytest.raises(RuntimeError):
        sync(store, [original], revision=1)
    assert original.metadata == {"nested": {"items": [1]}}
    assert snapshot(store) == before


def test_two_writers_same_revision_only_one_wins(store):
    barrier = Barrier(2)
    def run(text):
        barrier.wait(timeout=5)
        try:
            return sync(store, [doc(text=text)])
        except SourceRevisionConflict:
            return "conflict"
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(run, ["alpha", "beta"]))
    assert sum(isinstance(result, dict) for result in results) == 1
    assert results.count("conflict") == 1
    assert SQLiteSourceSynchronizer(store).inspect_source("source-A")["revision"] == 1


def test_busy_does_not_commit_callers_connection(store):
    synchronizer = SQLiteSourceSynchronizer(store, timeout=0)
    store.conn.execute("INSERT INTO documents VALUES ('pending','pending',1,'{}')")
    try:
        with pytest.raises(sqlite3.OperationalError, match="locked"):
            synchronizer.sync("source-A", [doc()], expected_revision=0, pipeline_revision="v1")
        assert store.conn.in_transaction
    finally:
        store.conn.rollback()
    assert SQLiteSourceSynchronizer(store).inspect_source("source-A")["revision"] == 0


def test_inspection_never_creates_manifest_tables(store):
    tables_before = store.conn.execute("SELECT name FROM sqlite_master ORDER BY name").fetchall()
    assert SQLiteSourceSynchronizer(store).inspect_source("new")["revision"] == 0
    assert store.conn.execute("SELECT name FROM sqlite_master ORDER BY name").fetchall() == tables_before


@pytest.mark.parametrize("documents", [[doc(), doc()], [Document(id="x", text=None)], [object()], "bad"])
def test_invalid_documents_no_database_changes(store, documents):
    with pytest.raises(ValueError):
        sync(store, documents)
    assert store.conn.execute("SELECT COUNT(*) FROM documents").fetchone() == (0,)


@pytest.mark.parametrize("options", [{"max_documents": True}, {"max_documents": 0},
    {"max_payload_chars": 0}, {"timeout": float("nan")}, {"timeout": True}, {"timeout": -1}])
def test_invalid_configuration(store, options):
    with pytest.raises(ValueError):
        SQLiteSourceSynchronizer(store, **options)


def test_payload_limit_and_metadata_serialization(store):
    with pytest.raises(ValueError, match="max_payload_chars"):
        SQLiteSourceSynchronizer(store, max_payload_chars=2).sync("A", [doc()], expected_revision=0, pipeline_revision="v1")
    with pytest.raises(ValueError):
        sync(store, [doc(value=float("nan"))])
    assert store.conn.execute("SELECT COUNT(*) FROM documents").fetchone() == (0,)


@pytest.mark.parametrize("kwargs", [
    {"source": " "}, {"expected_revision": True}, {"expected_revision": -1},
    {"pipeline_revision": ""}, {"allow_empty": 1},
])
def test_invalid_sync_options(store, kwargs):
    options = {"source": "A", "expected_revision": 0, "pipeline_revision": "v1"}
    options.update(kwargs)
    with pytest.raises(ValueError):
        SQLiteSourceSynchronizer(store).sync(documents=[doc()], **options)
    assert store.conn.execute("SELECT COUNT(*) FROM documents").fetchone() == (0,)


def test_first_transaction_failure_rolls_back_manifest_creation(store):
    with store.conn:
        store.conn.execute("""CREATE TRIGGER reject_first BEFORE INSERT ON documents
            BEGIN SELECT RAISE(ABORT, 'first failed'); END""")
    with pytest.raises(sqlite3.IntegrityError):
        sync(store, [doc()])
    tables = {r[0] for r in store.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "au_source_state_v1" not in tables
    assert "au_source_members_v1" not in tables
    assert SQLiteSourceSynchronizer(store).inspect_source("source-A")["revision"] == 0


def test_metadata_changes_are_persisted_and_reordering_keys_is_noop(store):
    sync(store, [doc(left=1, right=2)])
    assert sync(store, [doc(right=2, left=1)], revision=1)["revision"] == 1
    changed = sync(store, [doc(left=3, right=2)], revision=1)
    assert changed["updated"] == 1 and changed["revision"] == 2
    assert store.query(Query(query_str="alpha", keywords={"alpha"}))[0].metadata == {"left": 3, "right": 2}


def test_returned_terms_used_without_mutating_inputs_and_no_duplicate_index(store):
    original = doc()
    sync(store, [original])
    assert original.keywords == set()
    sync(store, [original], revision=1)
    assert store.conn.execute("SELECT term,COUNT(*) FROM inverted_index GROUP BY term").fetchall() == [("alpha", 1)]


def test_reject_memory_database_and_missing_schema(tmp_path):
    with pytest.raises(ValueError, match="file-backed"):
        SQLiteSourceSynchronizer(SQLiteStore(db_path=":memory:"))
    unrelated = tmp_path / "unrelated.db"
    with sqlite3.connect(unrelated) as connection:
        connection.execute("CREATE TABLE unrelated(value)")
    store = SQLiteStore(db_path=str(unrelated))
    with pytest.raises(sqlite3.OperationalError, match="documents"):
        SQLiteSourceSynchronizer(store).sync("A", [], expected_revision=0,
                                             pipeline_revision="v1", allow_empty=True)
    with sqlite3.connect(unrelated) as connection:
        assert connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == [("unrelated",)]


def test_pipeline_revision_changes_revision_without_rewriting_identical_rows(store):
    sync(store, [doc()])
    result = SQLiteSourceSynchronizer(store).sync("source-A", [doc()], expected_revision=1, pipeline_revision="v2")
    assert result["revision"] == 2 and result["unchanged"] == 1 and result["updated"] == 0


def test_real_component_manager_keyword_extraction_and_public_query(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.base.config.configer import Configer
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    managers = [StoreManager(), DocProcessorManager(), RagRouterManager()]
    pools = [dict(m._instance_obj_map) for m in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    instance = knowledge = None
    try:
        settings = Configer()
        settings.value = {"BASE_INFO": {"appname": "source-sync-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(settings)
        for manager in managers:
            manager._instance_obj_map.clear()
        instance = SQLiteStore(name="local", db_path=str(tmp_path / "real.db"), keyword_extractor="keywords")
        instance._new_client()
        for manager, component in zip(managers, [instance, JiebaKeywordExtractor(name="keywords"), BaseRouter(name="base_router")]):
            manager.register(component.get_instance_code(), component)
        real_store = managers[0].get_instance_obj("local", strict=True)
        first = sync(real_store, [doc(text="alpha manual")])
        sync(real_store, [doc(text="beta manual")], revision=first["revision"])
        instance.conn.close()
        instance._new_client()
        knowledge = Knowledge(stores=["local"])
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            assert knowledge.query_knowledge(query_str="alpha", keywords={"alpha"}) == []
            result = knowledge.query_knowledge(query_str="beta", keywords={"beta"})
        assert len(result) == 1 and result[0].text == "beta manual"
        assert result[0].id == first["document_ids"]["a"]
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if instance is not None:
            instance.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous
