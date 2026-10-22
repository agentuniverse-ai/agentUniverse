"""Actual Markdown file -> raw TxtReader -> Knowledge -> SQLite -> recall."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import agentuniverse.base.annotation.trace as trace_module
from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.doc_processor.table_header_splitter import TableHeaderSplitter
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


def test_documented_sqlite_example_without_manager_or_router_mocks():
    result = subprocess.run([sys.executable, "-m", "examples.table_header_sqlite_demo"],
                            cwd=Path(__file__).resolve().parents[6], capture_output=True,
                            text=True, timeout=60, check=False)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["fixture"] == "synthetic_parameter_table"
    assert report["stored_count"] > 1
    assert report["all_headers_retained"] is True
    ranges = sorted(chunk["rows"] for chunk in report["table_chunks"])
    assert ranges[0][0] == 0 and ranges[-1][1] == 12
    assert all(left[1] == right[0] for left, right in zip(ranges, ranges[1:]))
    assert all(chunk["file_name"] == "specifications.md" for chunk in report["table_chunks"])
    for i in range(12):
        assert sum(f"| alpha{i} | {i * 10} |" in chunk["text"] for chunk in report["table_chunks"]) == 1


def test_real_package_scan_registers_shipped_table_splitter(monkeypatch):
    from agentuniverse.base.agentuniverse import AgentUniverse
    from agentuniverse.base.component.component_enum import ComponentEnum
    from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.store.document import Document

    monkeypatch.setattr(ApplicationConfigManager(), "_ApplicationConfigManager__app_configer", AppConfiger())
    manager = DocProcessorManager()
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    app = AgentUniverse()
    configs = app.scan(["agentuniverse.agent.action.knowledge.doc_processor"],
                       ConfigTypeEnum.YAML, ComponentEnum.DOC_PROCESSOR)
    selected = [config for config in configs if config.name == "table_header_splitter"]
    assert len(selected) == 1
    app._AgentUniverse__register(ComponentEnum.DOC_PROCESSOR, selected)
    splitter = manager.get_instance_obj("table_header_splitter", strict=True)
    assert isinstance(splitter, TableHeaderSplitter)
    assert splitter.max_chars == 2000
    assert splitter.component_config_path.endswith("table_header_splitter.yaml")
    header = "| model | power (W) |\n| --- | --- |\n"
    source = header + "".join(f"| device-{i} | {i} |\n" for i in range(250))
    chunks = splitter.process_docs([Document(id="spec", text=source)])
    assert len(chunks) > 1
    assert all(chunk.text.startswith(header) for chunk in chunks)
    assert sum(chunk.metadata["table_chunk"]["row_end"] - chunk.metadata["table_chunk"]["row_start"] for chunk in chunks) == 250
    splitter.max_chars = 100
    assert manager.get_instance_obj("table_header_splitter", strict=True).max_chars == 2000


@pytest.mark.parametrize("enabled", [False, True])
def test_file_insert_persistence_and_retrieval_preserve_units(tmp_path, enabled):
    source = "# alpha specifications\n\n| model | power (W) |\n| --- | --- |\n" + "".join(
        f"| alpha{i} | {i * 10} |\n" for i in range(6))
    path = tmp_path / "specifications.md"
    path.write_text(source, encoding="utf-8")
    processors = {"split": TableHeaderSplitter(max_chars=90), "keywords": JiebaKeywordExtractor()}
    reader = TxtReader()
    store = SQLiteStore(db_path=str(tmp_path / "evidence.db"), keyword_extractor="keywords")
    knowledge = Knowledge(name="table-example", stores=["local"], readers={"md": "raw_text"},
                          insert_processors=["split"] if enabled else [])
    with patch.object(knowledge_module, "DocProcessorManager") as pm, \
            patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as sm, \
            patch.object(knowledge_module, "ReaderManager") as rm, \
            patch.object(knowledge_module, "StoreManager") as stm, \
            patch.object(knowledge_module, "RagRouterManager") as routers, \
            patch.object(trace_module, "ConversationMemoryModule"), \
            patch.object(trace_module, "Monitor") as monitor:
        pm.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
        sm.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
        rm.return_value.get_instance_obj.return_value = reader
        stm.return_value.get_instance_obj.return_value = store
        router = MagicMock()
        router.rag_route.return_value = [(Query(query_str="alpha", keywords={"alpha"}), "local")]
        routers.return_value.get_instance_obj.return_value = router
        monitor.get_invocation_chain.return_value = []
        try:
            store._new_client()
            knowledge.insert_knowledge(source_path=str(path))
            rm.return_value.get_instance_obj.assert_called_once_with("raw_text")
            rm.return_value.get_file_default_reader.assert_not_called()
            rows = store.conn.execute("SELECT metadata FROM documents").fetchall()
            assert len(rows) > 1 if enabled else len(rows) == 1
            if enabled:
                info = [json.loads(row[0])["table_chunk"] for row in rows]
                assert sum(item["row_end"] - item["row_start"] for item in info if item["kind"] == "table") == 6
            store.conn.close()
            store._new_client()
            recalled = knowledge.query_knowledge(query_str="alpha")
            assert recalled
            if enabled:
                tables = [doc for doc in recalled if doc.metadata["table_chunk"]["kind"] == "table"]
                assert len(tables) >= 2
                assert all("| model | power (W) |" in doc.text for doc in tables)
                assert all(doc.metadata["file_name"] == "specifications.md" for doc in tables)
                assert sum(doc.metadata["table_chunk"]["row_end"] - doc.metadata["table_chunk"]["row_start"] for doc in tables) == 6
            else:
                assert len(recalled) == 1 and recalled[0].text == source
                assert "table_chunk" not in recalled[0].metadata
        finally:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
            if store.conn is not None:
                store.conn.close()
