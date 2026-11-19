import asyncio
import shutil
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.store.fts5_store import SQLiteFTS5Store
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture
def store(tmp_path):
    configured = SQLiteFTS5Store(db_path=str(tmp_path / "fts.db"))
    configured._new_client()
    return configured


def query(text="alpha", **options):
    return Query(query_str=text, ext_info={"fts5": options})


def ids(documents):
    return [doc.id for doc in documents]


def test_full_text_persistence_and_roundtrip(store):
    document = Document(id="1", text="alpha beta gamma delta epsilon zeta", metadata={"nested": [1, None]}, embedding=[0.5], keywords={"alpha"})
    store.insert_document([document])
    reopened = SQLiteFTS5Store(db_path=store.db_path)
    reopened._new_client()
    found = reopened.query(query("zeta"))
    assert ids(found) == ["1"]  # indexed even though not in supplied keywords.
    assert found[0].text == document.text
    assert found[0].embedding == [0.5] and found[0].keywords == {"alpha"}
    assert found[0].metadata["nested"] == [1, None]
    assert found[0].metadata["__fts5"]["lower_is_better"] is True
    assert "__fts5" not in document.metadata
    found[0].metadata["nested"].append("changed")
    assert reopened.query(query("zeta"))[0].metadata["nested"] == [1, None]


def test_modes_and_literal_query_not_fts_program(store):
    store.insert_document([Document(id="a", text="alpha beta"), Document(id="b", text="beta alpha"),
                           Document(id="c", text="alpha"), Document(id="d", text="OR unrelated")])
    assert set(ids(store.query(query("alpha beta")))) == {"a", "b", "c"}
    assert set(ids(store.query(query("alpha beta", match_mode="all")))) == {"a", "b"}
    assert ids(store.query(query("alpha beta", match_mode="phrase"))) == ["a"]
    assert ids(store.query(query("OR"))) == ["d"]
    assert store.query(query('"')) == []
    assert store.query(query("   ")) == []


def test_ranking_ties_and_query_limit(store):
    store.insert_document([Document(id="b", text="alpha"), Document(id="a", text="alpha"),
                           Document(id="long", text="alpha " + "extra " * 100)])
    result = store.query(query())
    assert ids(result) == ["a", "b", "long"]
    scores = [doc.metadata["__fts5"]["bm25"] for doc in result]
    assert scores == sorted(scores)
    assert ids(store.query(Query(query_str="alpha", similarity_top_k=1))) == ["a"]
    with pytest.raises(ValueError, match="similarity_top_k"):
        store.query(Query(query_str="alpha", similarity_top_k=0))


def test_type_sensitive_metadata_equality_and_missing_null(store):
    values = [("null", None), ("true", True), ("integer", 1), ("real", 1.0), ("text", "1")]
    store.insert_document([Document(id=key, text="alpha", metadata={"value": value}) for key, value in values] + [Document(id="missing", text="alpha", metadata={})])
    for key, value in values:
        assert ids(store.query(query(metadata_equals={"value": value}))) == [key]


def test_all_write_modes_update_index_atomically(store):
    store.insert_document([Document(id="one", text="alpha")])
    with pytest.raises(sqlite3.IntegrityError):
        store.insert_document([Document(id="two", text="temporary"), Document(id="one", text="collision")])
    assert store.query(query("temporary")) == []
    assert ids(store.query(query())) == ["one"]
    with pytest.raises(KeyError):
        store.update_document([Document(id="one", text="modified"), Document(id="missing", text="bad")])
    assert ids(store.query(query())) == ["one"]
    store.upsert_document([Document(id="one", text="beta"), Document(id="two", text="beta")])
    assert store.query(query()) == []
    store.update_document([Document(id="one", text="gamma")])
    assert ids(store.query(query("beta"))) == ["two"]
    store.delete_document("two")
    assert store.query(query("beta")) == []
    store.delete_document("absent")
    assert ids(store.query(query("gamma"))) == ["one"]


def test_trigger_failure_rolls_back_rows_and_index(store):
    with sqlite3.connect(store.db_path) as db:
        db.execute("CREATE TRIGGER fail_test BEFORE INSERT ON au_fts_docs WHEN new.id='fail' BEGIN SELECT RAISE(ABORT,'fixture rejection'); END")
    with pytest.raises(sqlite3.IntegrityError, match="fixture rejection"):
        store.insert_document([Document(id="good", text="alpha"), Document(id="fail", text="beta")])
    assert store.query(query()) == []
    with sqlite3.connect(store.db_path) as db:
        assert db.execute("SELECT count(*) FROM au_fts_docs").fetchone()[0] == 0


@pytest.mark.parametrize("field,value", [("max_document_chars", 2), ("max_batch_chars", 2), ("max_batch_documents", 1)])
def test_write_budgets_leave_database_unchanged(store, field, value):
    setattr(store, field, value)
    with pytest.raises(ValueError):
        store.insert_document([Document(text="alpha"), Document(text="beta")])
    assert store.query(query()) == []


@pytest.mark.parametrize("options", [{"match_mode": "raw"}, {"unknown": 1}, {"metadata_equals": {"nested.key": 1}},
    {"metadata_equals": {"a": []}}, {"metadata_equals": {"a": float("nan")}}])
def test_bad_query_options(store, options):
    with pytest.raises(ValueError):
        store.query(query(**options))


def test_input_output_bounds_and_unsupported_vectors(store):
    store.insert_document([Document(text="alpha")])
    store.max_result_chars = 1
    with pytest.raises(ValueError, match="max_result_chars"):
        store.query(query())
    store.max_query_terms = 1
    with pytest.raises(ValueError, match="term budget"):
        store.query(query("alpha beta"))
    with pytest.raises(ValueError, match="vector"):
        store.query(Query(query_str="alpha", embeddings=[[0.5]]))
    with pytest.raises(ValueError, match="reserved"):
        store.insert_document([Document(text="alpha", metadata={"__fts5": {}})])


def test_duplicate_batch_and_nonfinite_payload_rejected(store):
    with pytest.raises(ValueError, match="duplicate"):
        store.upsert_document([Document(id="same", text="a"), Document(id="same", text="b")])
    with pytest.raises(ValueError):
        store.insert_document([Document(text="alpha", metadata={"not_json": float("inf")})])


def test_missing_database_is_not_created_by_query(tmp_path):
    path = tmp_path / "missing.db"
    with pytest.raises(sqlite3.OperationalError):
        SQLiteFTS5Store(db_path=str(path)).query(query())
    assert not path.exists()


def test_missing_schema_trigger_fails_without_repair(store):
    with sqlite3.connect(store.db_path) as db:
        db.execute("DROP TRIGGER au_fts_update")
    with pytest.raises(ValueError, match="triggers"):
        store._new_client()


def test_concurrent_writers_use_independent_connections(store):
    def write(number):
        store.upsert_document([Document(id=str(number), text="alpha")])
    with ThreadPoolExecutor(4) as workers:
        list(workers.map(write, range(12)))
    result = store.query(Query(query_str="alpha", similarity_top_k=20))
    assert len(result) == 12


def test_real_async_crud(store):
    async def scenario():
        await store.async_insert_document([Document(id="one", text="alpha")])
        assert ids(await store.async_query(query())) == ["one"]
        await store.async_upsert_document([Document(id="one", text="beta")])
        assert await store.async_query(query()) == []
        await store.async_update_document([Document(id="one", text="gamma")])
        assert ids(await store.async_query(query("gamma"))) == ["one"]
        await store.async_delete_document("one")
        assert await store.async_query(query("gamma")) == []
    asyncio.run(scenario())


def test_async_cancellation_joins_worker_and_rolls_back(store):
    # Pause between first and second real SQL row writes via a SQLite trigger UDF.
    entered, release = threading.Event(), threading.Event()
    original = sqlite3.connect
    def connect(*args, **kwargs):
        connection = original(*args, **kwargs)
        def pause():
            entered.set()
            assert release.wait(5)
            return 0
        connection.create_function("test_pause", 0, pause)
        return connection
    with original(store.db_path) as db:
        db.execute("CREATE TRIGGER pause_test AFTER INSERT ON au_fts_docs WHEN new.id='one' BEGIN SELECT test_pause(); END")
    async def scenario():
        pending = asyncio.create_task(store.async_insert_document([Document(id="one", text="alpha"), Document(id="two", text="alpha")]))
        try:
            assert await asyncio.to_thread(entered.wait, 5)
            pending.cancel()
            await asyncio.sleep(0)
        finally:
            release.set()
        with pytest.raises(asyncio.CancelledError):
            await pending
        assert store.query(query()) == []
    with patch("sqlite3.connect", connect):
        asyncio.run(scenario())


def test_repeated_async_delete_cancellation_waits_for_worker_and_preserves_index(store):
    store.insert_document([Document(id="one", text="alpha")])
    entered, release = threading.Event(), threading.Event()
    original = sqlite3.connect

    def connect(*args, **kwargs):
        connection = original(*args, **kwargs)

        def pause():
            entered.set()
            assert release.wait(5)
            return 0

        connection.create_function("test_delete_pause", 0, pause)
        return connection

    with original(store.db_path) as db:
        db.execute("CREATE TRIGGER pause_delete AFTER DELETE ON au_fts_docs BEGIN SELECT test_delete_pause(); END")

    async def scenario():
        pending = asyncio.create_task(store.async_delete_document("one"))
        try:
            assert await asyncio.to_thread(entered.wait, 5)
            for _ in range(2):
                pending.cancel()
                await asyncio.sleep(0)
                assert not pending.done(), "cancel must not abandon the connection-owning worker"
        finally:
            release.set()
        with pytest.raises(asyncio.CancelledError):
            await pending
        assert ids(store.query(query())) == ["one"]
        # Immediately acquiring the write lock demonstrates worker cleanup completed.
        with original(store.db_path, timeout=0) as db:
            db.execute("BEGIN IMMEDIATE")
            assert db.execute("SELECT id FROM au_fts_docs").fetchall() == [("one",)]

    with patch("sqlite3.connect", connect):
        asyncio.run(scenario())


@pytest.mark.parametrize("field,value", [("db_path", ":memory:"), ("max_vm_steps", 1), ("max_seconds", float("inf")),
    ("max_batch_documents", True), ("similarity_top_k", 0)])
def test_runtime_mutation_revalidated(store, field, value):
    setattr(store, field, value)
    with pytest.raises(ValueError):
        store.query(query())


def test_sqlite_vm_budget_interrupts_query_without_corrupting_database(store):
    store.insert_document([Document(id=str(index), text="alpha beta gamma") for index in range(200)])
    store.max_vm_steps = 1000
    with pytest.raises(sqlite3.OperationalError, match="interrupted"):
        store.query(Query(query_str="alpha", similarity_top_k=200))
    store.max_vm_steps = 5_000_000
    assert len(store.query(Query(query_str="alpha", similarity_top_k=200))) == 200


def test_trigram_chinese_substring_and_tokenizer_schema_contract(tmp_path):
    store = SQLiteFTS5Store(db_path=str(tmp_path / "chinese.db"), tokenizer="trigram")
    store._new_client()
    store.insert_document([Document(id="cn", text="机器学习系统运行手册")])
    assert ids(store.query(query("学习系统"))) == ["cn"]
    with pytest.raises(ValueError, match="three Unicode"):
        store.query(query("学习"))
    incompatible = SQLiteFTS5Store(db_path=store.db_path, tokenizer="unicode61")
    with pytest.raises(ValueError, match="schema"):
        incompatible._new_client()
    with pytest.raises(ValueError, match="tokenizer"):
        incompatible.query(query("学习系统"))
    assert ids(store.query(query("运行手册"))) == ["cn"]


def test_real_yaml_public_knowledge_roundtrip(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.base.config.configer import Configer
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE
    managers = [StoreManager(), ReaderManager(), RagRouterManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    callbacks = list(POST_FORK_QUEUE)
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge = None
    try:
        config = Configer()
        config.value = {"BASE_INFO": {"appname": "fts5-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(config)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[7]
        copied = tmp_path / "fts5.yaml"
        shutil.copyfile(root / "agentuniverse/agent/action/knowledge/store/fts5_store.yaml.example", copied)
        spec = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        spec.db_path = str(tmp_path / "pipeline.db")
        backend = SQLiteFTS5Store().initialize_by_component_configer(spec)
        backend._new_client()
        for manager, component in zip(managers, [backend, TxtReader(name="text"), BaseRouter(name="base_router")]):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["sqlite_fts5_store"], readers={"txt": "text"})
        path = tmp_path / "manual.txt"
        path.write_text("alpha beta gamma delta epsilon zeta", encoding="utf-8")
        knowledge.insert_knowledge(source_path=str(path))
        # Re-register a new instance against the same persisted database.
        managers[0].unregister(backend.get_instance_code())
        reopened = SQLiteFTS5Store().initialize_by_component_configer(spec)
        reopened._new_client()
        managers[0].register(reopened.get_instance_code(), reopened)
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="zeta")
            assert len(result) == 1 and result[0].text == path.read_text(encoding="utf-8")
            assert result[0].metadata["file_name"] == "manual.txt"
            assert result[0].metadata["__fts5"]["lower_is_better"] is True
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous
        POST_FORK_QUEUE[:] = callbacks
