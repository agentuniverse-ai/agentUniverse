"""Actual read-only source snapshots, identity and Knowledge insertion."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.file.sqlite_reader import SQLiteTableReader


def database(tmp_path):
    path = tmp_path / "source.db"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE products(id INTEGER PRIMARY KEY, description TEXT, category TEXT, secret BLOB)")
        connection.executemany("INSERT INTO products VALUES (?,?,?,?)", [
            (2, "beta manual", None, b"private"), (1, "alpha manual", "guide", b"private")])
    return path


def reader(**options):
    return SQLiteTableReader(table_name="products", **options)


def test_projection_types_keys_order_and_source_unchanged(tmp_path):
    path = database(tmp_path)
    before = path.read_bytes()
    result = reader(text_columns=["description"], metadata_columns=["category"], batch_size=1).load_data(path)
    assert [json.loads(d.text) for d in result] == [{"description": "alpha manual"}, {"description": "beta manual"}]
    assert [d.metadata["sqlite_key"] for d in result] == [{"id": 1}, {"id": 2}]
    assert result[1].metadata["sqlite_values"] == {"category": None}
    assert result[0].metadata["sqlite_declared_types"] == {"id": "INTEGER", "description": "TEXT", "category": "TEXT"}
    assert all("private" not in str(d.model_dump()) for d in result)
    assert len({d.metadata["sqlite_projection_sha256"] for d in result}) == 1
    assert path.read_bytes() == before


def test_ids_survive_updates_but_projection_fingerprint_changes(tmp_path):
    path = database(tmp_path)
    first = reader().load_data(path)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("UPDATE products SET description='updated' WHERE id=1")
    second = reader().load_data(path)
    assert [d.id for d in first] == [d.id for d in second]
    assert first[0].metadata["sqlite_projection_sha256"] != second[0].metadata["sqlite_projection_sha256"]
    assert second[0].metadata["sqlite_projection_sha256"] == reader().load_data(path)[0].metadata["sqlite_projection_sha256"]


def test_composite_primary_key_without_rowid_and_blob_values(tmp_path):
    path = tmp_path / "composite.db"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE products(region TEXT, code INTEGER, value BLOB, PRIMARY KEY(region,code)) WITHOUT ROWID")
        connection.executemany("INSERT INTO products VALUES (?,?,?)", [("B", 2, b"\x00\xff"), ("A", 1, None)])
    result = reader().load_data(path)
    assert [d.metadata["sqlite_key"] for d in result] == [{"region": "A", "code": 1}, {"region": "B", "code": 2}]
    assert json.loads(result[1].text)["value"] == {"base64": "AP8="}


def test_explicit_unique_ids_and_duplicate_null_rejection(tmp_path):
    path = tmp_path / "keys.db"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE products(code TEXT, value TEXT)")
        connection.execute("INSERT INTO products VALUES ('a','first')")
    with pytest.raises(ValueError, match="primary key"):
        reader().load_data(path)
    assert len(reader(id_columns=["code"]).load_data(path)) == 1
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("INSERT INTO products VALUES ('a','second')")
    with pytest.raises(ValueError, match="not unique"):
        reader(id_columns=["code"]).load_data(path)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("DELETE FROM products")
        connection.execute("INSERT INTO products VALUES (NULL,'missing')")
    with pytest.raises(ValueError, match="null"):
        reader(id_columns=["code"]).load_data(path)


def test_quoted_identifiers_are_literal_names(tmp_path):
    path = tmp_path / "quoted.db"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute('CREATE TABLE "product""s" ("key""id" TEXT PRIMARY KEY, "label text" TEXT)')
        connection.execute('INSERT INTO "product""s" VALUES (?,?)', ("one", "alpha"))
    result = SQLiteTableReader(table_name='product"s', text_columns=["label text"]).load_data(path)
    assert json.loads(result[0].text) == {"label text": "alpha"}
    assert result[0].metadata["sqlite_key"] == {'key"id': "one"}


@pytest.mark.parametrize("declaration,keys", [("TEXT COLLATE NOCASE", ["a", "A"]), ("", [1, 1.0])])
def test_distinct_encoded_keys_have_stable_order_despite_sql_sort_ties(tmp_path, declaration, keys):
    path = tmp_path / "tied-keys.db"
    rows = [(key, str(index)) for index, key in enumerate(keys)]
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE products(code " + declaration + ", value TEXT)")
        connection.executemany("INSERT INTO products VALUES (?,?)", rows)
    configured = reader(id_columns=["code"])
    first = configured.load_data(path)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("DELETE FROM products")
        connection.executemany("INSERT INTO products VALUES (?,?)", rows[::-1])
    second = configured.load_data(path)
    assert [doc.id for doc in first] == [doc.id for doc in second]
    assert first[0].metadata["sqlite_projection_sha256"] == second[0].metadata["sqlite_projection_sha256"]


def test_view_and_virtual_table_rejected(tmp_path):
    path = database(tmp_path)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE VIEW product_view AS SELECT * FROM products")
    with pytest.raises(ValueError, match="ordinary"):
        SQLiteTableReader(table_name="product_view").load_data(path)
    with pytest.raises(ValueError, match="ordinary"):
        SQLiteTableReader(table_name="sqlite_schema").load_data(path)
    # FTS may be omitted in other Python builds; ordinary/view checks still run.
    with closing(sqlite3.connect(path)) as connection, connection:
        try:
            connection.execute("CREATE VIRTUAL TABLE search USING fts5(content)")
        except sqlite3.OperationalError:
            return
    with pytest.raises(ValueError, match="ordinary"):
        SQLiteTableReader(table_name="search", id_columns=["content"]).load_data(path)


def test_read_transaction_preserves_snapshot_during_wal_update(tmp_path, monkeypatch):
    import agentuniverse.agent.action.knowledge.reader.file.sqlite_reader as module
    path = database(tmp_path)
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
    original = module._value
    changed = []
    def concurrent_write(value):
        if not changed:
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("UPDATE products SET description='new value' WHERE id=2")
            changed.append(True)
        return original(value)
    monkeypatch.setattr(module, "_value", concurrent_write)
    result = reader(text_columns=["description"], batch_size=1).load_data(path)
    assert json.loads(result[1].text)["description"] == "beta manual"
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("SELECT description FROM products WHERE id=2").fetchone() == ("new value",)


@pytest.mark.parametrize("options,match", [({"max_rows": 1}, "max_rows"),
    ({"max_file_bytes": 1}, "max_file_bytes"), ({"max_row_chars": 1}, "max_row_chars"),
    ({"max_output_chars": 1}, "max_output_chars"), ({"text_columns": ["missing"]}, "columns")])
def test_hard_limits_and_projection_fail_without_partial_output(tmp_path, options, match):
    path = database(tmp_path)
    with pytest.raises(ValueError, match=match):
        reader(**options).load_data(path)


def test_vm_budget_interrupts_expensive_sort(tmp_path):
    path = tmp_path / "many.db"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE products(code INTEGER, value TEXT)")
        connection.executemany("INSERT INTO products VALUES (?,?)", [(i, "value") for i in range(3000, 0, -1)])
    with pytest.raises(ValueError, match="budget"):
        reader(id_columns=["code"], max_vm_steps=1000).load_data(path)
    assert len(reader(id_columns=["code"]).load_data(path)) == 3000


def test_time_budget_rejects_incomplete_snapshot(tmp_path, monkeypatch):
    import agentuniverse.agent.action.knowledge.reader.file.sqlite_reader as module
    path = database(tmp_path)
    ticks = []
    def clock():
        ticks.append(1)
        return 0.0 if len(ticks) == 1 else 2.0
    monkeypatch.setattr(module.time, "monotonic", clock)
    with pytest.raises(ValueError, match="max_seconds|budget"):
        reader(max_seconds=1.0).load_data(path)


def test_projection_fingerprint_is_not_a_whole_database_hash(tmp_path):
    path = database(tmp_path)
    configured = reader(text_columns=["description"])
    first = configured.load_data(path)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("UPDATE products SET secret=?", (b"changed unseen",))
    second = configured.load_data(path)
    assert first[0].metadata["sqlite_projection_sha256"] == second[0].metadata["sqlite_projection_sha256"]


def test_old_sqlite_runtime_is_explicitly_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(sqlite3, "sqlite_version_info", (3, 36, 0))
    with pytest.raises(RuntimeError, match="3.37"):
        reader().load_data(tmp_path / "never-created.db")
    assert not (tmp_path / "never-created.db").exists()


@pytest.mark.parametrize("options", [{"batch_size": True}, {"max_rows": 0}, {"max_seconds": float("inf")},
    {"max_vm_steps": 1}, {"id_columns": ["id", "id"]}, {"text_columns": [""]}])
def test_bad_options(tmp_path, options):
    path = database(tmp_path)
    with pytest.raises(ValueError):
        reader(**options).load_data(path)


def test_missing_corrupt_empty_and_nonfinite(tmp_path):
    missing = tmp_path / "missing.db"
    with pytest.raises(FileNotFoundError):
        reader().load_data(missing)
    assert not missing.exists()
    missing.write_bytes(b"not SQLite")
    with pytest.raises(sqlite3.DatabaseError):
        reader().load_data(missing)
    path = database(tmp_path)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("DELETE FROM products")
    assert reader().load_data(path) == []
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("INSERT INTO products(id, secret) VALUES (1,?)", (float("inf"),))
    with pytest.raises(ValueError, match="non-finite"):
        reader().load_data(path)


def test_provenance_protected_and_metadata_not_shared(tmp_path):
    path = database(tmp_path)
    extra = {"nested": [1]}
    result = reader().load_data(path, ext_info=extra)
    result[0].metadata["nested"].append(2)
    assert extra == {"nested": [1]} and result[1].metadata["nested"] == [1]
    with pytest.raises(ValueError, match="provenance"):
        reader().load_data(path, ext_info={"sqlite_projection_sha256": "forged"})


def test_real_yaml_registration_source_to_target_retrieval(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.base.config.configer import Configer
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    managers = [ReaderManager(), StoreManager(), DocProcessorManager(), RagRouterManager()]
    pools = [dict(m._instance_obj_map) for m in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    target = knowledge = None
    source = database(tmp_path)
    source_before = source.read_bytes()
    try:
        settings = Configer()
        settings.value = {"BASE_INFO": {"appname": "sqlite-reader-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(settings)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[8]
        config = ComponentConfiger().load_by_configer(Configer(str(root /
            "agentuniverse/agent/action/knowledge/reader/file/sqlite_reader.yaml")).load())
        config.table_name = "products"
        config.text_columns = ["description"]
        config.metadata_columns = ["category"]
        registered = SQLiteTableReader().initialize_by_component_configer(config)
        target = SQLiteStore(name="target", db_path=str(tmp_path / "target.db"), keyword_extractor="keywords")
        target._new_client()
        for manager, component in zip(managers, [registered, target, JiebaKeywordExtractor(name="keywords"), BaseRouter(name="base_router")]):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["target"], readers={"db": "sqlite_table_reader"})
        knowledge.insert_knowledge(source_path=str(source))
        target.conn.close()
        target._new_client()
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="alpha", keywords={"alpha"})
        assert len(result) == 1 and json.loads(result[0].text) == {"description": "alpha manual"}
        assert result[0].metadata["sqlite_key"] == {"id": 1}
        assert result[0].metadata["sqlite_values"] == {"category": "guide"}
        assert source.read_bytes() == source_before
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if target is not None:
            target.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous
