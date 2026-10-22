"""Table preservation, boundary grammar and source identity contracts."""

import importlib
import inspect
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.table_header_splitter import TableHeaderSplitter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


HEADER = "| model | power (W) |\n| --- | ---: |\n"
ROWS = [f"| alpha{i} | {i * 10} |\n" for i in range(8)]


@pytest.mark.parametrize("budget", [1, 55, 100, 1000])
@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_all_rows_once_headers_context_and_exact_original_offsets(budget, newline):
    text = ("# Specifications\n\n" + HEADER + "".join(ROWS) + "\nTrailing prose.").replace("\n", newline)
    doc = Document(text=text, metadata={"source": "manual", "original": 7}, embedding=[1], keywords={"old"})
    before = doc.model_dump()
    chunks = TableHeaderSplitter(max_chars=budget).process_docs([doc])
    tables = [item for item in chunks if item.metadata["table_chunk"]["kind"] == "table"]
    reconstructed = ""
    expected_start = 0
    for item in tables:
        info = item.metadata["table_chunk"]
        assert info["row_start"] == expected_start
        expected_start = info["row_end"]
        data = text[info["source_start"]:info["source_end"]]
        assert item.text == info["heading_context"] + info["header_text"] + data
        assert info["header_text"] == HEADER.replace("\n", newline)
        assert info["heading_context"] == "# Specifications" + newline
        assert info["over_budget"] == (len(item.text) > budget)
        if info["over_budget"]:
            assert info["row_end"] - info["row_start"] == 1
        reconstructed += data
    assert reconstructed == "".join(ROWS).replace("\n", newline)
    assert expected_start == 8
    assert len({t.metadata["table_chunk"]["table_id"] for t in tables}) == 1
    assert all(not chunk.embedding and not chunk.keywords for chunk in chunks)
    assert len({chunk.id for chunk in chunks}) == len(chunks)
    assert doc.model_dump() == before


@pytest.mark.parametrize("table", [
    "a | b\n--- | :---:\nx | y", "| a\\|z | b |\n| --- | --- |\n| x\\|z | y |",
    "| 中文 | 金额（元） |\n| --- | --- |\n| 项目 | 12.5 |",
    "| a | b |\n| --- | --- |\n| x\\\\ | y |",
])
def test_supported_optional_borders_escapes_unicode_and_no_final_newline(table):
    result = TableHeaderSplitter(max_chars=1).process_docs([Document(text=table)])
    assert len(result) == 1 and result[0].text == table
    assert result[0].metadata["table_chunk"]["row_end"] == 1


@pytest.mark.parametrize("text", [
    "a | b\n- | -\nx | y\n", "| a | b |\n| --- | --- |\n| x | y | z |\n",
    "    | a | b |\n    | --- | --- |\n    | x | y |\n",
    "```markdown\n" + HEADER + ROWS[0] + "```\n",
    "~~~~\n" + HEADER + ROWS[0] + "~~~\n",  # Short fence does not close.
    "plain prose", "", None,
])
def test_unsupported_or_fenced_input_is_not_reinterpreted(text):
    doc = Document(id="source", text=text)
    assert TableHeaderSplitter().process_docs([doc])[0] is doc


def test_header_only_table_and_two_tables_never_mix():
    text = HEADER + "\n## Next\n| time | distance (km) |\n| --- | --- |\n| 1 | 10 |\n"
    result = TableHeaderSplitter(max_chars=1).process_docs([Document(text=text)])
    tables = [doc for doc in result if doc.metadata["table_chunk"]["kind"] == "table"]
    assert tables[0].metadata["table_chunk"]["row_start"] == tables[0].metadata["table_chunk"]["row_end"] == 0
    assert "power" not in tables[1].text and "distance" not in tables[0].text
    assert tables[0].metadata["table_chunk"]["table_id"] != tables[1].metadata["table_chunk"]["table_id"]


def test_stable_ids_across_reruns_distinct_sources_and_repeated_tables():
    text = HEADER + ROWS[0] + "\n" + HEADER + ROWS[0]
    processor = TableHeaderSplitter()
    a = Document(text=text, metadata={"source": "a"})
    b = Document(text=text, metadata={"source": "b"})
    first = processor.process_docs([a, b])
    assert len({doc.id for doc in first}) == len(first)
    assert [doc.id for doc in processor.process_docs([a, b])] == [doc.id for doc in first]


def test_unit_caption_paragraph_is_repeated_without_inventing_units():
    text = "# 财报\n\n单位：万元\n未经审计\n\n" + HEADER + "".join(ROWS)
    result = TableHeaderSplitter(max_chars=1).process_docs([Document(text=text)])
    tables = [doc for doc in result if doc.metadata["table_chunk"]["kind"] == "table"]
    assert len(tables) == len(ROWS)
    assert all(doc.metadata["table_chunk"]["preceding_context"] == "单位：万元\n未经审计\n" for doc in tables)
    assert all(doc.text.startswith("# 财报\n单位：万元\n未经审计\n" + HEADER) for doc in tables)


def test_valid_fence_close_then_table_and_heading_hierarchy():
    text = "# Root\n## Old\n~~~md\n" + HEADER + "~~~\n## New\n" + HEADER + ROWS[0]
    result = TableHeaderSplitter().process_docs([Document(text=text)])
    tables = [doc for doc in result if doc.metadata["table_chunk"]["kind"] == "table"]
    assert len(tables) == 1
    assert tables[0].metadata["table_chunk"]["heading_context"] == "# Root\n## New\n"
    assert tables[0].metadata["table_chunk"]["preceding_context"] == ""


@pytest.mark.parametrize("value", [0, -1, True, "50", 1.5])
def test_invalid_budget_constructor_yaml_runtime(value):
    with pytest.raises(ValueError):
        TableHeaderSplitter(max_chars=value)
    config = Configer(str(Path(inspect.getfile(TableHeaderSplitter)).with_suffix(".yaml"))).load()
    config.set("max_chars", value)
    processor = TableHeaderSplitter()
    with pytest.raises(ValueError):
        processor.initialize_by_component_configer(ComponentConfiger(config).load())
    assert processor.max_chars == 2000
    processor.max_chars = value
    with pytest.raises(ValueError):
        processor.process_docs([])


def test_real_yaml_class_and_reserved_metadata_collision():
    config = Configer(str(Path(inspect.getfile(TableHeaderSplitter)).with_suffix(".yaml"))).load()
    component = ComponentConfiger(config).load()
    cls = getattr(importlib.import_module(component.metadata_module), component.metadata_class)
    assert cls().initialize_by_component_configer(component).name == "table_header_splitter"
    with pytest.raises(ValueError, match="reserved"):
        TableHeaderSplitter().process_docs([Document(text=HEADER, metadata={"table_chunk": "user data"})])
