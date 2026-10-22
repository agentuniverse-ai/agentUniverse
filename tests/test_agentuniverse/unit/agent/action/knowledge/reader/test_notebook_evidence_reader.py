"""Real nbformat files and public Knowledge integration, no model calls."""

import hashlib
import json
import random
import shutil
import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.file.notebook_evidence_reader import NotebookEvidenceReader

nbformat = pytest.importorskip("nbformat")


def notebook(cells=None, minor=5):
    result = {"nbformat": 4, "nbformat_minor": minor, "metadata": {}, "cells": cells or []}
    if minor < 5:
        for cell in result["cells"]:
            cell.pop("id", None)
    return result


def markdown(text="Decision alpha", identifier="prose"):
    return {"cell_type": "markdown", "id": identifier, "metadata": {}, "source": text}


def code(text="print('alpha')", outputs=None, identifier="code", count=7):
    return {
        "cell_type": "code",
        "id": identifier,
        "metadata": {},
        "source": text,
        "execution_count": count,
        "outputs": outputs or [],
    }


def stream(text="alpha\n", name="stdout"):
    return {"output_type": "stream", "name": name, "text": text}


def save(tmp_path, value):
    path = tmp_path / "research.ipynb"
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def evidence(document):
    return document.metadata["notebook_evidence"]


@pytest.mark.parametrize("minor", range(6))
def test_supported_minors_without_conversion_or_id_repair(tmp_path, minor):
    value = notebook([markdown(["## Decision\n", "实验"], "m"), code("answer=42", count=None)], minor)
    nbformat.validate(deepcopy(value))
    path = save(tmp_path, value)
    before = path.read_bytes()
    docs = NotebookEvidenceReader().load_data(path)
    assert [doc.text for doc in docs] == ["## Decision\n实验", "answer=42"]
    assert evidence(docs[0])["cell_id"] == ("m" if minor == 5 else None)
    assert evidence(docs[1])["cell_key"] == ("id:code" if minor == 5 else "index:1")
    assert evidence(docs[1])["execution_count"] is None
    assert path.read_bytes() == before
    assert evidence(docs[0])["file_sha256"] == hashlib.sha256(before).hexdigest()


def test_output_opt_in_is_separate_from_source_and_execution_order(tmp_path):
    value = notebook([code("alpha = 1", [stream("old result")], "later", 30), code("alpha = 2", [], "earlier", 2)])
    value["cells"][0]["metadata"]["trusted"] = True
    path = save(tmp_path, value)
    reader = NotebookEvidenceReader()
    docs, report = reader.load_notebook(path)
    assert [doc.text for doc in docs] == ["alpha = 1", "alpha = 2"]
    assert report["omitted_outputs"] == [{"json_pointer": "/cells/0/outputs/0", "reason": "text_outputs_disabled"}]
    enabled = NotebookEvidenceReader(include_text_outputs=True).load_data(path)
    assert [evidence(doc)["kind"] for doc in enabled] == ["source", "cached_output", "source"]
    assert enabled[0].id == docs[0].id and enabled[2].id == docs[1].id
    assert enabled[1].text.endswith("old result") and "UNVERIFIED" in enabled[1].text
    assert evidence(enabled[1])["source_document_id"] == enabled[0].id
    assert evidence(enabled[1])["execution_verified"] is False
    assert evidence(enabled[1])["cache_status"] == "unverified"
    assert [evidence(enabled[i])["execution_count"] for i in (0, 2)] == [30, 2]


def test_mime_selection_errors_and_attachments_are_explicit(tmp_path):
    outputs = [
        stream(["first\n", "second\n"], "stderr"),
        {
            "output_type": "display_data",
            "metadata": {},
            "data": {"text/plain": ["42", "\n"], "text/html": "<b>42</b>", "image/png": "AAAA"},
        },
        {"output_type": "execute_result", "metadata": {}, "execution_count": 9, "data": {"text/plain": "43"}},
        {"output_type": "display_data", "metadata": {}, "data": {"text/html": "<b>no plaintext</b>"}},
        {"output_type": "error", "ename": "ValueError", "evalue": "invalid trial", "traceback": ["line1", "line2"]},
    ]
    prose = markdown("![figure](attachment:figure.png)")
    prose["attachments"] = {"figure.png": {"image/png": "AAAA"}}
    path = save(tmp_path, notebook([prose, code(outputs=outputs)]))
    reader = NotebookEvidenceReader(include_text_outputs=True)
    docs, report = reader.load_notebook(path)
    assert len(docs) == 5
    assert evidence(docs[0])["attachment_names"] == ["figure.png"]
    assert docs[2].text.endswith("first\nsecond\n")
    assert evidence(docs[2])["stream_name"] == "stderr"
    assert evidence(docs[3])["available_mime_types"] == ["image/png", "text/html", "text/plain"]
    assert "<b>" not in docs[3].text and "AAAA" not in docs[3].text
    assert evidence(docs[4])["output_execution_count"] == 9
    assert {item["reason"] for item in report["omitted_outputs"]} == {
        "error_outputs_disabled",
        "no_plain_text_representation",
    }
    errors = NotebookEvidenceReader(include_error_outputs=True).load_data(path)
    assert len(errors) == 3
    assert errors[-1].text.endswith("ValueError: invalid trial\nline1\nline2")
    assert evidence(errors[-1])["output_type"] == "error"


def test_empty_and_raw_cells_keep_exact_source(tmp_path):
    raw = {"cell_type": "raw", "metadata": {"format": "text/html"}, "id": "raw", "source": "<p>raw text</p>"}
    docs = NotebookEvidenceReader().load_data(
        save(tmp_path, notebook([markdown(""), raw, code("", identifier="empty")]))
    )
    assert [doc.text for doc in docs] == ["", "<p>raw text</p>", ""]
    assert len({doc.id for doc in docs}) == 3
    assert evidence(docs[1])["cell_type"] == "raw"


def test_snapshot_ids_namespace_and_metadata_isolation(tmp_path):
    path = save(tmp_path, notebook([markdown("same", "one"), markdown("same", "two")]))
    reader = NotebookEvidenceReader()
    info = {"team": {"names": ["research"]}}
    docs = reader.load_data(path, notebook_id="experiment-1", ext_info=info)
    assert len({doc.id for doc in docs}) == 2
    other = tmp_path / "copy.ipynb"
    shutil.copyfile(path, other)
    assert [doc.id for doc in reader.load_data(other, notebook_id="experiment-1")] == [doc.id for doc in docs]
    assert reader.load_data(other)[0].id != reader.load_data(path)[0].id
    assert reader.load_data(path, notebook_id="experiment-2")[0].id != docs[0].id
    docs[0].metadata["team"]["names"].append("changed")
    assert docs[1].metadata["team"] == info["team"] == {"names": ["research"]}
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert reader.load_data(path, notebook_id="experiment-1")[0].id != docs[0].id


@pytest.mark.parametrize(
    "mutate,match",
    [
        (lambda nb: nb.update(nbformat=3), "Only nbformat"),
        (lambda nb: nb.update(nbformat_minor=6), "Only nbformat"),
        (lambda nb: nb.update(nbformat_minor=True), "Only nbformat"),
        (lambda nb: nb["cells"][0].pop("id"), "missing or invalid id"),
        (lambda nb: nb["cells"][0].update(id="bad id"), "missing or invalid id"),
        (lambda nb: nb["cells"].append(deepcopy(nb["cells"][0])), "duplicate id"),
        (lambda nb: nb["cells"][0].update(source=[3]), "Invalid notebook schema"),
        (lambda nb: nb["cells"][0].update(outputs=[]), "Invalid notebook schema"),
        (lambda nb: nb["cells"][0].update(cell_type="future"), "Invalid notebook schema"),
    ],
)
def test_bad_notebooks_fail_without_repair(tmp_path, mutate, match):
    value = notebook([markdown()])
    mutate(value)
    path = save(tmp_path, value)
    before = path.read_bytes()
    with pytest.raises(ValueError, match=match):
        NotebookEvidenceReader().load_data(path)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "content", ['{"cells": [], "cells": []}', '{"x": NaN}', '{"x": 1e9999}', "[]", "{}", "{bad json"]
)
def test_strict_json(tmp_path, content):
    path = tmp_path / "invalid.ipynb"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        NotebookEvidenceReader().load_data(path)


@pytest.mark.parametrize(
    "options,match",
    [
        ({"max_file_bytes": 10}, "max_file_bytes"),
        ({"max_cells": 1}, "max_cells"),
        ({"max_outputs": 1}, "max_outputs"),
        ({"max_source_chars": 2}, "max_source_chars"),
        ({"max_output_chars": 2, "include_text_outputs": True}, "max_output_chars"),
        ({"max_total_chars": 2}, "max_total_chars"),
    ],
)
def test_limits_return_no_partial_result(tmp_path, options, match):
    path = save(tmp_path, notebook([markdown(), code(outputs=[stream(), stream()])]))
    with pytest.raises(ValueError, match=match):
        NotebookEvidenceReader(**options).load_data(path)


@pytest.mark.parametrize(
    "options",
    [
        {"max_cells": 0},
        {"max_cells": True},
        {"max_outputs": "3"},
        {"include_text_outputs": "false"},
        {"max_file_bytes": 100000001},
    ],
)
def test_invalid_settings(tmp_path, options):
    with pytest.raises(ValueError):
        NotebookEvidenceReader(**options).load_data(save(tmp_path, notebook()))


def test_yaml_settings_validate_before_mutation():
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    config = Configer()
    config.value = {"name": "changed", "include_text_outputs": "false"}
    component = ComponentConfiger().load_by_configer(config)
    reader = NotebookEvidenceReader(name="original")
    with pytest.raises(ValueError, match="boolean"):
        reader._initialize_by_component_configer(component)
    assert reader.name == "original" and reader.include_text_outputs is False


def test_bad_metadata_id_and_extension(tmp_path):
    path = save(tmp_path, notebook())
    for extra in ([], {"notebook_evidence": {}}):
        with pytest.raises(ValueError):
            NotebookEvidenceReader().load_data(path, ext_info=extra)
    for identifier in ("", "  ", 1, "x" * 4097):
        with pytest.raises(ValueError):
            NotebookEvidenceReader().load_data(path, notebook_id=identifier)
    with pytest.raises(ValueError, match=".ipynb"):
        NotebookEvidenceReader().load_data(tmp_path / "data.json")


def test_missing_optional_dependency_and_reader_does_not_import_execution_stack(tmp_path, monkeypatch):
    path = save(tmp_path, notebook([code("raise AssertionError('must never execute')")]))
    for module in ("nbclient", "jupyter_client", "ipykernel"):
        monkeypatch.setitem(sys.modules, module, None)
    docs = NotebookEvidenceReader().load_data(path)
    assert len(docs) == 1 and docs[0].text.startswith("raise AssertionError")
    monkeypatch.setitem(sys.modules, "nbformat", None)
    with pytest.raises(ImportError, match="notebook_ext"):
        NotebookEvidenceReader().load_data(path)


def test_nbformat_validation_does_not_mutate_parsed_object(tmp_path, monkeypatch):
    original = nbformat.validate
    seen = []

    def check(value, **kwargs):
        before = deepcopy(value)
        original(value, **kwargs)
        assert value == before
        seen.append(True)

    monkeypatch.setattr(nbformat, "validate", check)
    for minor in range(6):
        NotebookEvidenceReader().load_data(save(tmp_path, notebook([markdown()], minor)))
    assert len(seen) == 6


def test_sixty_seeded_notebooks_against_nbformat_normalized_text(tmp_path):
    rng = random.Random(2301)
    for trial in range(60):
        cells = []
        for index in range(rng.randrange(1, 15)):
            source = "\n".join(rng.choices(["alpha", "实验", "", "x = 42", "# heading"], k=4))
            if rng.choice([True, False]):
                source = source.splitlines(keepends=True)
            if rng.choice([True, False]):
                cells.append(markdown(source, f"c{index}"))
            else:
                cells.append(code(source, [stream(["one\n", "two"])], f"c{index}", rng.choice([None, 2, 9])))
        path = save(tmp_path, notebook(cells))
        oracle = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        nbformat.validate(oracle)
        docs = NotebookEvidenceReader(include_text_outputs=True).load_data(path)
        sources = [doc for doc in docs if evidence(doc)["kind"] == "source"]
        assert [doc.text for doc in sources] == [cell.source for cell in oracle.cells], trial
        assert len({doc.id for doc in docs}) == len(docs)
        for doc in docs:
            item = evidence(doc)
            assert item["text_sha256"] == hashlib.sha256(doc.text.encode("utf-8")).hexdigest()
            if item["kind"] == "cached_output":
                assert item["source_document_id"] == sources[item["cell_index"]].id


def test_real_yaml_public_knowledge_sqlite_roundtrip(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    path = save(
        tmp_path, notebook([markdown("alpha research evidence"), code("result = 42", [stream("stale result")])])
    )
    managers = [ReaderManager(), StoreManager(), RagRouterManager(), DocProcessorManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge, store = None, None
    try:
        app = Configer()
        app.value = {"BASE_INFO": {"appname": "notebook-evidence-test"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/file/notebook_evidence_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = NotebookEvidenceReader().initialize_by_component_configer(config)
        store = SQLiteStore(
            name="notebook_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="notebook_keywords"
        )
        store._new_client()
        components = [
            reader,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="notebook_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["notebook_store"], readers={"ipynb": "notebook_evidence_reader"})
        knowledge.insert_knowledge(source_path=str(path))
        assert store.conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 2
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="alpha")
        assert len(result) == 1 and "alpha research" in result[0].text
        assert evidence(result[0])["json_pointer"] == "/cells/0/source"
        assert evidence(result[0])["file_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None and store.conn is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous
