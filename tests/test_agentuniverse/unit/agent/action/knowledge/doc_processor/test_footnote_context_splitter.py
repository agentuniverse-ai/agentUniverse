"""Exact source evidence and footnote-preserving ingestion contracts."""
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.footnote_context_splitter import FootnoteContextSplitter as Splitter
from agentuniverse.agent.action.knowledge.store.document import Document


def split(text, **options):
    return Splitter(**options).process_docs([Document(text=text, metadata={"source": "fixture"})])


def test_body_reference_carries_remote_definition_and_exact_offsets():
    text = "Voltage is 12 V[^v].\r\n\r\nUnrelated paragraph.\r\n\r\n[^v]: Only at 20°C.\r\n    Tolerance is 5%.\r\n"
    result = split(text, chunk_chars=25)
    body = result[0]
    note = body.metadata["footnote_context"]["definitions"][0]
    assert note["appended"] is True
    assert body.text[slice(*note["output_span"])] == text[slice(*note["source_span"])]
    assert "Tolerance is 5%" in body.text
    assert "Unrelated" not in body.text
    assert "".join(text[slice(*d.metadata["footnote_context"]["source_span"])] for d in result) == text
    for item in result:
        for reference in item.metadata["footnote_context"]["references"]:
            assert text[slice(*reference["source_span"])] == "[^v]"


def test_same_chunk_definition_is_not_duplicated():
    text = "Body[^a] and again[^a].\n\n[^a]: Definition.\n"
    result = split(text)[0]
    assert result.text == text
    assert len(result.metadata["footnote_context"]["references"]) == 2
    assert len(result.metadata["footnote_context"]["definitions"]) == 1
    assert result.metadata["footnote_context"]["definitions"][0]["appended"] is False


def test_mult_paragraph_definition_kept_intact():
    text = "Body[^a].\n\n[^a]: First.\n\n    Second paragraph.\n\nOther."
    result = split(text, chunk_chars=10)
    assert "[^a]: First.\n\n    Second paragraph." in result[0].text
    assert "Other." not in result[0].text


@pytest.mark.parametrize("code", ["`[^a]`", "``x ` [^a]``", "`multi\n[^a]`",
                                  "```md\n[^a]\n```", "~~~\n[^a]\n~~~", "    [^a]", "\t[^a]"])
def test_code_markers_not_linked(code):
    result = split(code + "\n\n[^a]: hidden", chunk_chars=5)
    assert all(not d.metadata["footnote_context"]["references"] for d in result)


def test_fenced_fake_definition_does_not_resolve_real_reference():
    result = split("Body[^a].\n\n```\n[^a]: fake\n```", chunk_chars=10)
    assert result[0].metadata["footnote_context"]["unresolved"] == ["a"]


@pytest.mark.parametrize("separator", ["\n\n", "\n\n```\ncode\n```\n\n", "\n\n[^b]: definition\n\n"])
def test_unmatched_inline_code_does_not_hide_later_paragraph_reference(separator):
    text = "Unmatched `" + separator + "Body[^a] ` literal\n\n[^a]: real"
    result = split(text, chunk_chars=10)
    references = [reference for item in result for reference in item.metadata["footnote_context"]["references"]]
    assert [r["label"] for r in references] == ["a"]


def test_multiple_notes_follow_first_reference_order_without_repeat():
    text = "Body[^b][^a][^b].\n\n[^a]: first\n\n[^b]: second"
    body = split(text, chunk_chars=20)[0]
    notes = body.metadata["footnote_context"]["definitions"]
    assert [n["label"] for n in notes] == ["b", "a"]
    assert body.text.count("[^b]: second") == 1
    for note in notes:
        assert body.text[slice(*note["output_span"])] == text[slice(*note["source_span"])]


def test_escaped_markers_and_case_sensitive_labels():
    result = split(r"Ignore \[^a], resolve [^a], miss [^A]." + "\n\n[^a]: note")[0]
    context = result.metadata["footnote_context"]
    assert [r["label"] for r in context["references"]] == ["a", "A"]
    assert context["unresolved"] == ["A"]


def test_missing_error_and_duplicate_definition_fail():
    with pytest.raises(ValueError, match="unresolved"):
        split("Body[^a].", missing="error")
    with pytest.raises(ValueError, match="duplicate"):
        split("[^a]: first\n\n[^a]: second")


def test_input_is_unchanged_and_source_isolation_and_stable_ids():
    text = "Body[^a].\n\n[^a]: note"
    original = Document(id="fixed", text=text, metadata={"source": "A", "nested": [1]},
                        embedding=[1.0], keywords={"old"})
    before = original.model_dump()
    processor = Splitter(chunk_chars=10)
    first = processor.process_docs([original])
    assert [d.id for d in first] == [d.id for d in processor.process_docs([original])]
    other = original.model_copy(update={"metadata": {"source": "B"}})
    assert set(d.id for d in first).isdisjoint(d.id for d in processor.process_docs([other]))
    first[0].metadata["nested"].append(2)
    assert original.model_dump() == before
    assert all(not d.embedding and not d.keywords for d in first)
    with pytest.raises(ValueError, match="already present"):
        processor.process_docs(first)


def test_definitions_do_not_cross_input_documents():
    result = Splitter().process_docs([Document(text="Body[^a]"), Document(text="[^a]: elsewhere")])
    assert result[0].metadata["footnote_context"]["unresolved"] == ["a"]


@pytest.mark.parametrize("options", [{"chunk_chars": 0}, {"chunk_chars": True},
    {"max_document_chars": 1}, {"max_output_chars": 5}, {"max_references": 1},
    {"missing": "guess"}, {"source_key": ""}])
def test_limits_and_options(options):
    with pytest.raises(ValueError):
        split("Body[^a][^a].\n\n[^a]: note", **options)


def test_append_budget_and_batch_budget_are_hard():
    with pytest.raises(ValueError, match="max_output_chars"):
        split("Body[^a].\n\n[^a]: long definition here", chunk_chars=10, max_output_chars=20)
    with pytest.raises(ValueError, match="max_output_chars"):
        Splitter(max_output_chars=5).process_docs([Document(text="aaa"), Document(text="bbb")])


def test_unreferenced_definition_empty_and_oversize_paragraph_are_preserved():
    for text in ("", "[^a]: unreferenced", "a" * 50):
        result = split(text, chunk_chars=10)
        assert "".join(d.text for d in result) == text
    assert split("a" * 50, chunk_chars=10)[0].metadata["footnote_context"]["over_chunk_target"] is True


def test_real_managers_file_insert_reopen_and_query(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
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
        app = Configer()
        app.value = {"BASE_INFO": {"appname": "footnote-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[7]
        config = ComponentConfiger().load_by_configer(Configer(str(root /
            "agentuniverse/agent/action/knowledge/doc_processor/footnote_context_splitter.yaml")).load())
        splitter = Splitter().initialize_by_component_configer(config)
        splitter.chunk_chars = 30
        splitter.source_key = "file_name"
        reader = TxtReader(name="raw_text")
        keywords = JiebaKeywordExtractor(name="keywords")
        router = BaseRouter(name="base_router")
        store = SQLiteStore(name="local", db_path=str(tmp_path / "notes.db"), keyword_extractor="keywords")
        store._new_client()
        for manager, component in [(managers[0], reader), (managers[1], store),
                                   (managers[2], splitter), (managers[2], keywords), (managers[3], router)]:
            manager.register(component.get_instance_code(), component)
        source = tmp_path / "notes.md"
        source.write_text("Voltage alpha[^a].\n\nUnrelated section.\n\n[^a]: Only at 20°C.", encoding="utf-8")
        knowledge = Knowledge(stores=["local"], readers={"md": "raw_text"},
                              insert_processors=["footnote_context_splitter"])
        knowledge.insert_knowledge(source_path=str(source))
        store.conn.close()
        store._new_client()
        with patch.object(trace_module, "ConversationMemoryModule"), \
                patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="alpha", keywords={"alpha"})
        assert len(result) == 1
        assert "Only at 20°C" in result[0].text
        assert "Unrelated" not in result[0].text
        assert result[0].metadata["footnote_context"]["definitions"][0]["appended"] is True
        assert result[0].metadata["footnote_context"]["source_id"] == source.name
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
