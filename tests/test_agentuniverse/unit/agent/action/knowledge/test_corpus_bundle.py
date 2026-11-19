"""Real ZIP/JSON corruption and public Knowledge round-trip tests."""

import hashlib
import json
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.corpus_bundle import export_bundle, load_bundle
from agentuniverse.agent.action.knowledge.reader.file.corpus_bundle_reader import CorpusBundleReader
from agentuniverse.agent.action.knowledge.store.document import Document


def make(tmp_path, name="bundle.auc", **kwargs):
    path = tmp_path / name
    docs = [
        Document(
            id="a",
            text="alpha evidence 中文",
            keywords={"alpha"},
            embedding=[1.0],
            metadata={"secret": "excluded", "page": 2},
        ),
        Document(id="b", text="beta evidence"),
    ]
    digest = export_bundle(
        path,
        docs,
        sources={"source-1": "alpha evidence 中文\nbeta evidence"},
        document_sources={"a": ["source-1"], "b": ["source-1"]},
        **kwargs,
    )
    return path, digest


def rewrite(path, change, *, compression=zipfile.ZIP_STORED):
    with zipfile.ZipFile(path) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(members["manifest.json"])
    change(manifest, members)
    members["manifest.json"] = json.dumps(manifest).encode()
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        for name, data in members.items():
            archive.writestr(name, data)


def test_portable_roundtrip_and_default_privacy(tmp_path):
    path, digest = make(tmp_path)
    before = path.read_bytes()
    other = tmp_path / "other"
    other.mkdir()
    moved = other / "renamed.auc"
    shutil.copyfile(path, moved)
    docs = load_bundle(moved, expected_sha256=digest)
    assert [d.id for d in docs] == ["a", "b"]
    assert docs[0].text == "alpha evidence 中文"
    assert docs[0].keywords == {"alpha"}
    assert docs[0].embedding == []
    assert set(docs[0].metadata) == {"_corpus_bundle"}
    assert docs[0].metadata["_corpus_bundle"]["sha256"] == digest
    assert docs[0].metadata["_corpus_bundle"]["sources"] == {
        "source-1": hashlib.sha256("alpha evidence 中文\nbeta evidence".encode()).hexdigest()
    }
    assert path.read_bytes() == before
    assert b"excluded" not in before and str(tmp_path).encode() not in before


def test_explicit_metadata_allowlist_and_determinism(tmp_path):
    a, _ = make(tmp_path, "a.auc", metadata_keys=["page"])
    b, _ = make(tmp_path, "b.auc", metadata_keys=["page"])
    assert a.read_bytes() == b.read_bytes()
    assert load_bundle(a)[0].metadata["page"] == 2
    assert "secret" not in load_bundle(a)[0].metadata


@pytest.mark.parametrize(
    "change",
    [
        lambda m, e: m.update(version=2),
        lambda m, e: m.update(version=True),
        lambda m, e: m.update(format="other"),
        lambda m, e: m.update(extra=True),
        lambda m, e: m["documents"][1].update(id="a"),
        lambda m, e: m["documents"][0].update(sources=["absent"]),
        lambda m, e: m["documents"][0].update(sources=["source-1", "source-1"]),
        lambda m, e: m["documents"][0].update(sources=[]),
        lambda m, e: m["documents"][0].update(member="../outside.json"),
        lambda m, e: m["sources"].append(m["sources"][0]),
        lambda m, e: e.update({"documents/1.json": b"tampered"}),
        lambda m, e: e.update({"sources/0.txt": b"tampered"}),
        lambda m, e: e.pop("documents/1.json"),
        lambda m, e: e.update({"extra.txt": b"extra"}),
    ],
)
def test_whole_bundle_validation(tmp_path, change):
    path, _ = make(tmp_path)
    rewrite(path, change)
    with pytest.raises(ValueError):
        load_bundle(path)


@pytest.mark.parametrize(
    "change",
    [
        lambda p: p.update(id="wrong"),
        lambda p: p.update(text=12),
        lambda p: p.update(keywords=["x", "x"]),
        lambda p: p.update(metadata={"_corpus_bundle": {"sha256": "forged"}}),
        lambda p: p.update(embedding=[1.0]),
    ],
)
def test_rehashed_invalid_document_rejected(tmp_path, change):
    path, _ = make(tmp_path)

    def alter(manifest, entries):
        payload = json.loads(entries["documents/1.json"])
        change(payload)
        data = json.dumps(payload).encode()
        entries["documents/1.json"] = data
        manifest["documents"][1]["sha256"] = hashlib.sha256(data).hexdigest()

    rewrite(path, alter)
    with pytest.raises(ValueError):
        load_bundle(path)


def test_duplicate_json_keys_and_zip_entries(tmp_path):
    path, _ = make(tmp_path)
    with zipfile.ZipFile(path, "a") as archive:
        with pytest.warns(UserWarning):
            archive.writestr("manifest.json", b'{"version":1,"version":1}')
    with pytest.raises(ValueError):
        load_bundle(path)
    path2 = tmp_path / "json.auc"
    with zipfile.ZipFile(path2, "w") as archive:
        archive.writestr("manifest.json", b'{"version":1,"version":1}')
    with pytest.raises(ValueError, match="duplicate JSON"):
        load_bundle(path2)


def test_hash_compression_truncation_and_limits(tmp_path):
    path, _ = make(tmp_path)
    with pytest.raises(ValueError, match="digest"):
        load_bundle(path, expected_sha256="0" * 64)
    for kwargs in [{"max_bytes": 1}, {"max_documents": 1}, {"max_sources": 0}]:
        with pytest.raises(ValueError):
            load_bundle(path, **kwargs)
    rewrite(path, lambda m, e: None, compression=zipfile.ZIP_DEFLATED)
    with pytest.raises(ValueError, match="stored ZIP"):
        load_bundle(path)
    path.write_bytes(path.read_bytes()[:100])
    with pytest.raises(ValueError):
        load_bundle(path)


@pytest.mark.parametrize(
    "kwargs", [{"max_bytes": 1}, {"max_documents": 1}, {"metadata_keys": "page"}, {"metadata_keys": ["_corpus_bundle"]}]
)
def test_invalid_export_leaves_no_destination(tmp_path, kwargs):
    with pytest.raises(ValueError):
        make(tmp_path, **kwargs)
    assert list(tmp_path.iterdir()) == []


def test_source_and_document_validation(tmp_path):
    doc = Document(id="a", text="text")
    cases = [
        ([doc, doc], {"s": "text"}, {"a": ["s"]}),
        ([doc], {"s": "text"}, {"a": ["missing"]}),
        ([doc], {"s": "text"}, {"a": ["s"], "extra": ["s"]}),
        ([doc], {"s": 1}, {"a": ["s"]}),
    ]
    for docs, sources, links in cases:
        with pytest.raises(ValueError):
            export_bundle(tmp_path / "bad.auc", docs, sources=sources, document_sources=links)
    assert list(tmp_path.iterdir()) == []


def test_atomic_no_overwrite_and_concurrent_publication(tmp_path):
    def publish(_):
        try:
            make(tmp_path)
            return "ok"
        except FileExistsError:
            return "exists"

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(publish, range(4)))
    assert results.count("ok") == 1 and results.count("exists") == 3
    assert len(load_bundle(tmp_path / "bundle.auc")) == 2
    assert len(list(tmp_path.iterdir())) == 1


def test_failed_publish_removes_only_temp(tmp_path):
    with patch("os.link", side_effect=OSError("unsupported filesystem")):
        with pytest.raises(OSError):
            make(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_non_json_metadata_fails_only_if_selected(tmp_path):
    doc = Document(id="a", text="text", metadata={"object": object()})
    export_bundle(tmp_path / "safe.auc", [doc], sources={"s": "text"}, document_sources={"a": ["s"]})
    with pytest.raises(TypeError):
        export_bundle(
            tmp_path / "bad.auc", [doc], sources={"s": "text"}, document_sources={"a": ["s"]}, metadata_keys=["object"]
        )
    assert not (tmp_path / "bad.auc").exists()


def test_real_yaml_knowledge_sqlite_and_failed_import(tmp_path):
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

    path, digest = make(tmp_path)
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
        app.value = {"BASE_INFO": {"appname": "bundle-test"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/file/corpus_bundle_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = CorpusBundleReader().initialize_by_component_configer(config)
        store = SQLiteStore(
            name="bundle_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="bundle_keywords"
        )
        store._new_client()
        components = [
            reader,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="bundle_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["bundle_store"], readers={"auc": "corpus_bundle_reader"})
        # A late damaged document must not cause earlier documents to be inserted.
        damaged = tmp_path / "damaged.auc"
        shutil.copyfile(path, damaged)
        rewrite(damaged, lambda m, e: e.update({"documents/1.json": b"damaged"}))
        with pytest.raises(ValueError):
            knowledge.insert_knowledge(source_path=str(damaged))
        assert store.conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 0
        knowledge.insert_knowledge(source_path=str(path))
        assert store.conn.execute("SELECT count(*) FROM documents").fetchone()[0] == 2
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="alpha")
        assert len(result) == 1 and result[0].text == "alpha evidence 中文"
        assert result[0].metadata["_corpus_bundle"]["sha256"] == digest
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


def test_independently_authored_v1_package(tmp_path):
    source = b"independent source"
    payload = b'{"id":"reference","text":"independent source","metadata":{},"keywords":[]}'
    manifest = {
        "format": "agentuniverse-document-bundle",
        "version": 1,
        "sources": [{"id": "stable-source", "member": "sources/0.txt", "sha256": hashlib.sha256(source).hexdigest()}],
        "documents": [
            {
                "id": "reference",
                "member": "documents/0.json",
                "sha256": hashlib.sha256(payload).hexdigest(),
                "sources": ["stable-source"],
            }
        ],
    }
    path = tmp_path / "independent.auc"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("sources/0.txt", source)
        archive.writestr("documents/0.json", payload)
    assert load_bundle(path)[0].text == "independent source"


def test_exponent_overflow_in_metadata(tmp_path):
    path, _ = make(tmp_path)

    def alter(manifest, entries):
        data = b'{"id":"a","text":"text","metadata":{"value":1e999},"keywords":[]}'
        entries["documents/0.json"] = data
        manifest["documents"][0]["sha256"] = hashlib.sha256(data).hexdigest()

    rewrite(path, alter)
    with pytest.raises(ValueError):
        load_bundle(path)


def test_empty_bundle_and_reader_bounds(tmp_path):
    path = tmp_path / "empty.auc"
    export_bundle(path, [], sources={}, document_sources={})
    assert load_bundle(path) == []
    with pytest.raises(ValueError):
        CorpusBundleReader(max_bytes=True)
