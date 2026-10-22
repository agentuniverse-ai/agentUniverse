"""Real Parquet projections, source identity and registered ingestion."""
import builtins
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")

from agentuniverse.agent.action.knowledge.reader.file.parquet_reader import ParquetReader  # noqa: E402


def write(tmp_path, rows=None, name="fixture.parquet"):
    path = tmp_path / name
    if rows is None:
        rows = [{"id": 1, "text": "alpha manual", "category": "guide", "ignored": "private"},
                {"id": 2, "text": "beta manual", "category": "spec", "ignored": "private"},
                {"id": 3, "text": "gamma manual", "category": None, "ignored": "private"}]
    pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=2)
    return path


def test_projection_row_groups_and_metadata_are_exact(tmp_path):
    path = write(tmp_path)
    reader = ParquetReader(text_columns=["text"], metadata_columns=["category"], batch_size=1)
    result = reader.load_data(path)
    assert [json.loads(d.text) for d in result] == [{"text": "alpha manual"}, {"text": "beta manual"}, {"text": "gamma manual"}]
    assert [d.metadata["parquet_row"] for d in result] == [0, 1, 2]
    assert [d.metadata["parquet_row_group"] for d in result] == [0, 0, 1]
    assert result[2].metadata["parquet_values"] == {"category": None}
    assert result[0].metadata["parquet_column_types"] == {"text": "string", "category": "string"}
    assert all("private" not in str(d.model_dump()) for d in result)
    assert len({d.id for d in result}) == 3
    assert [d.id for d in result] == [d.id for d in reader.load_data(path)]


def test_typed_nested_binary_temporal_and_decimal_values(tmp_path):
    path = write(tmp_path, [{"amount": Decimal("1.2300"), "timestamp": datetime(2026, 1, 2, tzinfo=timezone.utc),
                            "binary": b"\x00\xff", "nested": {"labels": ["中文", None]}, "flag": False}])
    row = ParquetReader().load_data(path)[0]
    data = json.loads(row.text)
    assert data["amount"] == "1.2300"
    assert data["timestamp"] == "2026-01-02T00:00:00+00:00"
    assert data["binary"] == {"base64": "AP8="}
    assert data["nested"] == {"labels": ["中文", None]}
    assert data["flag"] is False
    assert "decimal128" in row.metadata["parquet_column_types"]["amount"]


def test_nanosecond_temporals_are_exact_including_nested_values(tmp_path):
    path = tmp_path / "nanoseconds.parquet"
    clock = pa.array([123456789], type=pa.time64("ns"))
    table = pa.table({"timestamp": pa.array([123456789], type=pa.timestamp("ns", tz="UTC")),
                      "duration": pa.array([123456789], type=pa.duration("ns")),
                      "nested": pa.StructArray.from_arrays([clock], names=["clock"])})
    pq.write_table(table, path)
    data = json.loads(ParquetReader().load_data(path)[0].text)
    assert data["timestamp"] == {"epoch_nanoseconds": 123456789, "timezone": "UTC"}
    assert data["duration"] == {"nanoseconds": 123456789}
    assert data["nested"] == {"clock": {"nanoseconds_since_midnight": 123456789}}


def test_arrow_map_pair_order_and_nested_nulls(tmp_path):
    path = tmp_path / "map.parquet"
    table = pa.table({"mapping": pa.array([[('a', 1), ('a', 2)]], type=pa.map_(pa.string(), pa.int64())),
                      "values": pa.array([[1, None, 3]], type=pa.list_(pa.int64()))})
    pq.write_table(table, path)
    data = json.loads(ParquetReader().load_data(path)[0].text)
    assert data == {"mapping": [["a", 1], ["a", 2]], "values": [1, None, 3]}


def test_explicit_ids_survive_row_reordering_and_data_revision(tmp_path):
    path = write(tmp_path)
    reader = ParquetReader(id_column="id", text_columns=["text"])
    before = {d.metadata["parquet_original_id"]: d for d in reader.load_data(path)}
    write(tmp_path, [{"id": 2, "text": "updated"}, {"id": 1, "text": "unchanged"}])
    after = {d.metadata["parquet_original_id"]: d for d in reader.load_data(path)}
    assert before[1].id == after[1].id and before[2].id == after[2].id
    assert before[1].metadata["file_sha256"] != after[1].metadata["file_sha256"]
    assert after[1].metadata["parquet_row"] == 1


def test_default_ids_are_snapshot_specific_and_separate_sources(tmp_path):
    first, other = write(tmp_path), write(tmp_path, name="other.parquet")
    reader = ParquetReader()
    before = reader.load_data(first)
    assert {d.id for d in before}.isdisjoint(d.id for d in reader.load_data(other))
    write(tmp_path, [{"id": 1, "text": "changed"}])
    assert before[0].id != reader.load_data(first)[0].id


@pytest.mark.parametrize("ids", [[1, 1], [None, 2], [True, False], ["", "x"]])
def test_bad_or_duplicate_row_ids_fail_without_partial_return(tmp_path, ids):
    path = write(tmp_path, [{"id": identity, "text": "content"} for identity in ids])
    with pytest.raises(ValueError):
        ParquetReader(id_column="id").load_data(path)
    path.rename(tmp_path / "closed.parquet")  # no file handle retained after failure


@pytest.mark.parametrize("options", [{"text_columns": ["missing"]}, {"metadata_columns": ["missing"]},
    {"id_column": "missing"}, {"text_columns": ["text", "text"]}, {"batch_size": True},
    {"max_rows": 0}, {"max_file_bytes": -1}])
def test_invalid_configuration_or_columns(tmp_path, options):
    path = write(tmp_path)
    with pytest.raises(ValueError):
        ParquetReader(**options).load_data(path)


@pytest.mark.parametrize("options,match", [({"max_file_bytes": 10}, "max_file_bytes"),
    ({"max_rows": 2}, "max_rows"), ({"max_row_chars": 10}, "max_row_chars"),
    ({"max_output_chars": 10}, "max_output_chars")])
def test_resource_limits_reject_not_truncate(tmp_path, options, match):
    with pytest.raises(ValueError, match=match):
        ParquetReader(**options).load_data(write(tmp_path))


def test_corrupt_empty_and_duplicate_schema(tmp_path):
    corrupt = tmp_path / "corrupt.parquet"
    corrupt.write_bytes(b"not a parquet file")
    with pytest.raises(Exception):
        ParquetReader().load_data(corrupt)
    empty = tmp_path / "empty.parquet"
    pq.write_table(pa.table({"text": pa.array([], type=pa.string())}), empty)
    assert ParquetReader().load_data(empty) == []
    duplicate = tmp_path / "duplicate.parquet"
    pq.write_table(pa.Table.from_arrays([pa.array([1]), pa.array([2])], names=["x", "x"]), duplicate)
    with pytest.raises(ValueError, match="duplicate"):
        ParquetReader().load_data(duplicate)


def test_nonfinite_values_are_not_silently_lost(tmp_path):
    path = write(tmp_path, [{"value": float("nan")}])
    with pytest.raises(ValueError, match="non-finite"):
        ParquetReader().load_data(path)


def test_ext_info_is_copied_and_cannot_forge_provenance(tmp_path):
    path = write(tmp_path)
    extra = {"nested": [1]}
    result = ParquetReader().load_data(path, ext_info=extra)
    result[0].metadata["nested"].append(2)
    assert extra == {"nested": [1]}
    assert result[1].metadata["nested"] == [1]
    with pytest.raises(ValueError, match="provenance"):
        ParquetReader().load_data(path, ext_info={"parquet_row": 99})


def test_optional_dependency_has_clear_error(tmp_path, monkeypatch):
    original_import = builtins.__import__
    def missing(name, *args, **kwargs):
        if name.startswith("pyarrow"):
            raise ImportError("not installed")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", missing)
    with pytest.raises(ImportError, match="requires pyarrow"):
        ParquetReader().load_data(tmp_path / "unused.parquet")


def test_real_yaml_managers_insert_reopen_and_query(tmp_path):
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
    store = knowledge = None
    try:
        settings = Configer()
        settings.value = {"BASE_INFO": {"appname": "parquet-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(settings)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[8]
        config = ComponentConfiger().load_by_configer(Configer(str(root /
            "agentuniverse/agent/action/knowledge/reader/file/parquet_reader.yaml")).load())
        config.text_columns = ["text"]
        config.metadata_columns = ["category"]
        config.id_column = "id"
        reader = ParquetReader().initialize_by_component_configer(config)
        store = SQLiteStore(name="local", db_path=str(tmp_path / "rows.db"), keyword_extractor="keywords")
        store._new_client()
        for manager, component in zip(managers, [reader, store, JiebaKeywordExtractor(name="keywords"), BaseRouter(name="base_router")]):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["local"], readers={"parquet": "parquet_reader"})
        source = write(tmp_path)
        knowledge.insert_knowledge(source_path=str(source))
        store.conn.close()
        store._new_client()
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="alpha", keywords={"alpha"})
        assert len(result) == 1
        assert json.loads(result[0].text) == {"text": "alpha manual"}
        assert result[0].metadata["parquet_values"] == {"category": "guide"}
        assert result[0].metadata["parquet_original_id"] == 1
        assert result[0].metadata["source"] == source.resolve().as_uri()
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous
