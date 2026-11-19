"""Real PDF extraction tests; no fake pdfplumber tables."""
import hashlib
import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from agentuniverse.agent.action.knowledge.reader.file.pdf_table_reader import PdfTableContinuationReader

ROOT = Path(__file__).resolve().parents[8]
make_fixture = runpy.run_path(str(ROOT / "docs/examples/pdf_table_fixture.py"))["make_fixture"]


def test_actual_continuation_and_provenance(tmp_path):
    path = make_fixture(tmp_path / "table.pdf")
    before = path.read_bytes()
    extra = {"nested": {"owner": "test"}}
    reader = PdfTableContinuationReader()
    docs = reader.load_data(path, ext_info=extra)
    assert len(docs) == 1
    assert json.loads(docs[0].text) == {
        "header": ["Item", "Value"],
        "rows": [["alpha", "12"], ["beta", "15"], ["gamma", "16"], ["delta", "18"], ["epsilon", "20"]],
    }
    segments = docs[0].metadata["pdf_table_segments"]
    assert [segment["page"] for segment in segments] == [1, 2]
    assert [segment["row_range"] for segment in segments] == [[0, 3], [3, 5]]
    assert all(segment["header"] == ["Item", "Value"] for segment in segments)
    assert docs[0].metadata["file_sha256"] == hashlib.sha256(before).hexdigest()
    assert docs[0].metadata["source"] == path.as_uri()
    assert docs[0].id == reader.load_data(path)[0].id
    docs[0].metadata["nested"]["owner"] = "changed"
    assert extra["nested"]["owner"] == "test"
    assert path.read_bytes() == before


@pytest.mark.parametrize("options", [
    {"second_caption": "Table 2 (continued)"},
    {"second_caption": "Table 1: Independent table"},
    {"second_caption": "Table 1 (discontinued)"},
    {"second_header": ("Item", "Different unit")},
    {"second_x": 75},
    {"second_top": 620},
    {"first_top": 300},
    {"blank_page": True},
])
def test_ambiguous_or_independent_tables_not_joined(tmp_path, options):
    docs = PdfTableContinuationReader().load_data(make_fixture(tmp_path / "table.pdf", **options))
    assert len(docs) == 2
    assert sum(len(json.loads(doc.text)["rows"]) for doc in docs) == 5
    assert all(len(doc.metadata["pdf_table_segments"]) == 1 for doc in docs)


@pytest.mark.parametrize("option,value,match", [
    ("max_file_bytes", 10, "max_file_bytes"),
    ("max_pages", 1, "max_pages"),
    ("max_tables", 1, "max_tables"),
    ("max_cells", 2, "max_cells"),
    ("max_page_chars", 1, "character/edge"),
    ("max_page_edges", 1, "character/edge"),
    ("max_output_chars", 1, "max_output_chars"),
])
def test_resource_limits(tmp_path, option, value, match):
    path = make_fixture(tmp_path / "table.pdf")
    with pytest.raises(ValueError, match=match):
        PdfTableContinuationReader(**{option: value}).load_data(path)


@pytest.mark.parametrize("option,value", [("max_pages", True), ("edge_margin", float("nan")),
                                         ("caption_prefix", ""), ("continuation_marker", " ")])
def test_runtime_mutation_revalidated(tmp_path, option, value):
    reader = PdfTableContinuationReader()
    setattr(reader, option, value)
    with pytest.raises(ValueError):
        reader.load_data(make_fixture(tmp_path / "table.pdf"))


def test_reserved_metadata_and_empty_pdf(tmp_path):
    from reportlab.pdfgen import canvas
    path = tmp_path / "empty.pdf"
    pdf = canvas.Canvas(str(path))
    pdf.drawString(50, 750, "Prose is intentionally outside this reader's output contract.")
    pdf.showPage()
    pdf.save()
    reader = PdfTableContinuationReader()
    assert reader.load_data(path) == []
    with pytest.raises(ValueError, match="provenance"):
        reader.load_data(path, ext_info={"source": "forged"})


@pytest.mark.parametrize("merged_middle_cell", [False, True])
def test_three_page_chain_and_merged_cell_guard(tmp_path, merged_middle_cell):
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    path = tmp_path / "three-pages.pdf"
    pdf = canvas.Canvas(str(path), pagesize=(612, 792))
    for page, data_rows, top in [(1, 3, 170), (2, 26, 720), (3, 2, 720)]:
        caption = "Table 1" + (" (continued)" if page > 1 else "")
        pdf.drawString(50, top + 20, caption)
        rows = [["Item", "Value"]] + [[f"page{page}row{i}", str(i)] for i in range(data_rows)]
        table = Table(rows, colWidths=[220, 220], rowHeights=24)
        style = [("GRID", (0, 0), (-1, -1), 1, colors.black)]
        if merged_middle_cell and page == 2:
            style.append(("SPAN", (0, 1), (1, 1)))
        table.setStyle(TableStyle(style))
        table.wrap(440, 792)
        table.drawOn(pdf, 50, top - len(rows) * 24)
        pdf.showPage()
    pdf.save()
    docs = PdfTableContinuationReader().load_data(path)
    assert len(docs) == (3 if merged_middle_cell else 1)
    assert sum(len(json.loads(doc.text)["rows"]) for doc in docs) == 31
    if not merged_middle_cell:
        assert [part["row_range"] for part in docs[0].metadata["pdf_table_segments"]] == [[0, 3], [3, 29], [29, 31]]
    else:
        assert docs[1].metadata["pdf_table_segments"][0]["eligible"] is False
        assert json.loads(docs[1].text)["rows"][0][1] is None


def test_corrupt_pdf_rejected_and_source_released(tmp_path):
    path = tmp_path / "invalid.pdf"
    path.write_bytes(b"not a PDF")
    with pytest.raises(Exception, match="PDF|pdf|No /Root"):
        PdfTableContinuationReader().load_data(path)
    # On Windows an unreleased file handle would prevent this rename.
    moved = path.rename(tmp_path / "moved.pdf")
    assert moved.read_bytes() == b"not a PDF"


@pytest.mark.parametrize("keyword_limit,expected_count", [(3, 0), (100, 1)])
def test_real_yaml_registration_pdf_to_persisted_retrieval(tmp_path, keyword_limit, expected_count):
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
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    target = knowledge = None
    source = make_fixture(tmp_path / "table.pdf")
    try:
        settings = Configer()
        settings.value = {"BASE_INFO": {"appname": "pdf-table-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(settings)
        for manager in managers:
            manager._instance_obj_map.clear()
        config = ComponentConfiger().load_by_configer(Configer(str(ROOT /
            "agentuniverse/agent/action/knowledge/reader/file/pdf_table_reader.yaml")).load())
        registered = PdfTableContinuationReader().initialize_by_component_configer(config)
        target = SQLiteStore(name="target", db_path=str(tmp_path / "target.db"), keyword_extractor="keywords")
        target._new_client()
        for manager, component in zip(managers, [registered, target, JiebaKeywordExtractor(name="keywords", top_k=keyword_limit), BaseRouter(name="base_router")]):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["target"], readers={"pdf": "pdf_table_continuation_reader"})
        knowledge.insert_knowledge(source_path=str(source))
        target.conn.close()
        target._new_client()
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="delta", keywords={"delta"})
        assert len(result) == expected_count
        if not expected_count:
            # The ordinary default indexes only three keywords. Reader output is
            # intact, but it cannot promise retrieval of an unindexed row token.
            stored = target.conn.execute("SELECT text FROM documents").fetchall()
            assert len(stored) == 1 and "delta" in stored[0][0]
            return
        assert "alpha" in result[0].text and "delta" in result[0].text
        assert [part["page"] for part in result[0].metadata["pdf_table_segments"]] == [1, 2]
        assert len(json.loads(result[0].text)["rows"]) == 5
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
