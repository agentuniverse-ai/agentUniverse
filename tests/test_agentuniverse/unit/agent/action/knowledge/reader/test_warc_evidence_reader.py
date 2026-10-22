"""Real WARCWriter archives, independent expected bodies, no live website fetch."""

import gzip
import hashlib
import io
import shutil
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.reader.file.warc_evidence_reader import WarcEvidenceReader

pytest.importorskip("warcio")
from warcio.bufferedreaders import ChunkedDataException
from warcio.exceptions import ArchiveLoadFailed
from warcio.statusandheaders import StatusAndHeaders
from warcio.warcwriter import WARCWriter


def response(
    writer,
    text=b"alpha archived evidence",
    identifier="one",
    date="2026-01-01T00:00:00Z",
    media="text/plain; charset=utf-8",
    extra=None,
    warc=None,
    status="200 OK",
):
    headers = [("Content-Type", media)] + (extra or [])
    wh = {"WARC-Record-ID": f"<urn:test:{identifier}>", "WARC-Date": date}
    wh.update(warc or {})
    return writer.create_warc_record(
        "https://example.invalid/research",
        "response",
        payload=io.BytesIO(text),
        http_headers=StatusAndHeaders(status, headers, protocol="HTTP/1.1"),
        warc_headers_dict=wh,
    )


def revisit(writer, source, identifier="again", reference=True, **overrides):
    headers = {
        "WARC-Record-ID": f"<urn:test:{identifier}>",
        "WARC-Date": "2026-02-01T00:00:00Z",
        "WARC-Profile": "http://netpreserve.org/warc/1.1/revisit/identical-payload-digest",
        "WARC-Payload-Digest": source.rec_headers.get_header("WARC-Payload-Digest"),
    }
    if reference:
        headers["WARC-Refers-To"] = source.rec_headers.get_header("WARC-Record-ID")
    headers.update(overrides)
    return writer.create_warc_record(
        "https://example.invalid/research",
        "revisit",
        payload=io.BytesIO(b""),
        http_headers=StatusAndHeaders("200 OK", [], protocol="HTTP/1.1"),
        warc_headers_dict=headers,
    )


def archive(tmp_path, build=None, compressed=False, version="1.1"):
    path = tmp_path / ("archive.warc.gz" if compressed else "archive.warc")
    with path.open("wb") as stream:
        writer = WARCWriter(stream, gzip=compressed, warc_version=version)
        records = build(writer) if build else [response(writer)]
        for record in records:
            writer.write_record(record)
    return path


def evidence(doc):
    return doc.metadata["warc_evidence"]


@pytest.mark.parametrize("version", ["1.0", "1.1"])
@pytest.mark.parametrize("compressed", [False, True])
def test_real_archive_versions_and_compression(tmp_path, version, compressed):
    path = archive(tmp_path, compressed=compressed, version=version)
    original = path.read_bytes()
    docs, report = WarcEvidenceReader().load_archive(path)
    assert len(docs) == 1 and docs[0].text == "alpha archived evidence"
    info = evidence(docs[0])
    assert info["target_uri"] == "https://example.invalid/research"
    assert info["capture_date"] == "2026-01-01T00:00:00Z"
    assert info["digest_verification"] == "passed"
    assert info["decoded_payload_sha256"] == hashlib.sha256(b"alpha archived evidence").hexdigest()
    assert report["archive_sha256"] == hashlib.sha256(original).hexdigest()
    assert path.read_bytes() == original
    assert [doc.id for doc in WarcEvidenceReader().load_data(path)] == [docs[0].id]


def test_html_and_declared_charset(tmp_path):
    path = archive(
        tmp_path,
        lambda w: [
            response(
                w,
                b"<h1>History</h1><p>caf\xe9</p><script>ignored()</script><style>p{}</style>",
                media="text/html; charset=iso-8859-1",
            )
        ],
    )
    docs = WarcEvidenceReader().load_data(path)
    assert docs[0].text == "History\ncafé"
    assert evidence(docs[0])["representation"] == "html_derived_text"
    assert evidence(docs[0])["charset_source"] == "http_header"


def test_http_gzip_and_strict_chunked(tmp_path):
    compressed = gzip.compress("历史 alpha".encode())
    chunks = b"5\r\nalpha\r\n4\r\n old\r\n0\r\n\r\n"
    path = archive(
        tmp_path,
        lambda w: [
            response(
                w, compressed, "gzip", extra=[("Content-Encoding", "gzip"), ("Content-Length", str(len(compressed)))]
            ),
            response(w, chunks, "chunks", extra=[("Transfer-Encoding", "chunked")]),
        ],
    )
    assert [doc.text for doc in WarcEvidenceReader().load_data(path)] == ["历史 alpha", "alpha old"]


def test_revisit_resolves_same_archive_out_of_order_without_current_fetch(tmp_path, monkeypatch):
    def build(writer):
        source = response(writer)
        return [revisit(writer, source), source]

    path = archive(tmp_path, build, compressed=True)
    # Reader's network-independent path needs none of the HTTP client modules.
    monkeypatch.setitem(sys.modules, "requests", None)
    docs, report = WarcEvidenceReader().load_archive(path)
    assert [doc.text for doc in docs] == ["alpha archived evidence"] * 2
    assert len({doc.id for doc in docs}) == 2 and report["omitted_records"] == []
    info = evidence(docs[0])
    assert info["record_type"] == "revisit"
    assert info["capture_date"] == "2026-02-01T00:00:00Z"
    assert info["payload_source_capture_date"] == "2026-01-01T00:00:00Z"
    assert info["payload_source_record_id"] == "<urn:test:one>"
    assert info["revisit_resolution"] == "exact_record_id_and_verified_digest"


@pytest.mark.parametrize(
    "overrides,expected",
    [
        ({"WARC-Refers-To": "<urn:test:missing>"}, "revisit_source_unavailable"),
        ({"WARC-Profile": "http://netpreserve.org/warc/1.1/server-not-modified"}, "unsupported_revisit_profile"),
        ({"WARC-Payload-Digest": "sha1:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}, "revisit_digest_not_verified"),
        ({"WARC-Refers-To-Date": "2000-01-01T00:00:00Z"}, "revisit_reference_disagrees"),
        ({"WARC-Refers-To-Target-URI": "https://example.invalid/other"}, "revisit_reference_disagrees"),
    ],
)
def test_revisit_missing_or_disagreeing_evidence_is_not_fabricated(tmp_path, overrides, expected):
    def build(writer):
        source = response(writer)
        return [source, revisit(writer, source, **overrides)]

    docs, report = WarcEvidenceReader().load_archive(archive(tmp_path, build))
    assert len(docs) == 1
    assert report["omitted_records"][0]["reason"] == expected


def test_record_types_status_media_and_truncation_are_reported(tmp_path):
    def build(writer):
        return [
            response(writer),
            response(writer, identifier="image", media="image/png"),
            response(writer, identifier="404", status="404 Not Found"),
            response(writer, identifier="cut", warc={"WARC-Truncated": "length"}),
            response(writer, identifier="segment", warc={"WARC-Segment-Number": "1"}),
            response(writer, identifier="br", extra=[("Content-Encoding", "br")]),
            writer.create_warc_record("https://example.invalid", "metadata", payload=io.BytesIO(b"metadata")),
        ]

    docs, report = WarcEvidenceReader().load_archive(archive(tmp_path, build))
    assert len(docs) == 1 and report["record_count"] == 7
    assert {item["reason"] for item in report["omitted_records"]} == {
        "unsupported_media_type",
        "non_success_http_status",
        "truncated_or_segmented_record",
        "unsupported_http_encoding",
        "unsupported_record_type",
    }


def test_digest_mismatch_and_truncated_body_fail_without_partial_results(tmp_path):
    path = archive(tmp_path)
    original = path.read_bytes()
    path.write_bytes(original.replace(b"alpha archived evidence", b"omega archived evidence"))
    with pytest.raises(ArchiveLoadFailed, match="digest"):
        WarcEvidenceReader().load_data(path)
    path.write_bytes(original[: original.index(b"alpha archived evidence") + 5])
    with pytest.raises(ValueError, match="Truncated"):
        WarcEvidenceReader().load_data(path)


@pytest.mark.parametrize(
    "body,extra,error",
    [
        (b"alpha", [("Content-Length", "30")], ValueError),
        (b"x\r\nbody\r\n0\r\n\r\n", [("Transfer-Encoding", "chunked")], ChunkedDataException),
        (b"5\r\nabc", [("Transfer-Encoding", "chunked")], ChunkedDataException),
        (b"not gzip", [("Content-Encoding", "gzip")], gzip.BadGzipFile),
        (b"\xff", [], ValueError),
    ],
)
def test_invalid_encoded_response_is_not_reinterpreted(tmp_path, body, extra, error):
    path = archive(tmp_path, lambda w: [response(w, body, extra=extra)])
    with pytest.raises(error):
        WarcEvidenceReader().load_data(path)


def test_partial_response_and_malformed_media_are_explicitly_omitted(tmp_path):
    path = archive(
        tmp_path,
        lambda w: [
            response(w, identifier="206", status="206 Partial Content"),
            response(w, identifier="range", extra=[("Content-Range", "bytes 1-5/20")]),
            response(w, identifier="media", media="not-a-media-type"),
        ],
    )
    docs, report = WarcEvidenceReader().load_archive(path)
    assert docs == []
    assert [row["reason"] for row in report["omitted_records"]] == [
        "partial_http_response",
        "partial_http_response",
        "unsupported_media_type",
    ]


def test_gzip_crc_damage_and_expansion_limit(tmp_path):
    path = archive(tmp_path, compressed=True)
    data = bytearray(path.read_bytes())
    data[-8] ^= 1
    path.write_bytes(data)
    with pytest.raises(gzip.BadGzipFile):
        WarcEvidenceReader().load_data(path)
    path = archive(tmp_path, lambda w: [response(w, gzip.compress(b"a" * 10000), extra=[("Content-Encoding", "gzip")])])
    with pytest.raises(ValueError, match="byte limit"):
        WarcEvidenceReader(max_payload_bytes=100).load_data(path)


def test_revisit_never_resolves_by_url_or_chain(tmp_path):
    def build(writer):
        source = response(writer)
        first = revisit(writer, source)
        second = revisit(writer, source, identifier="third", **{"WARC-Refers-To": "<urn:test:again>"})
        missing = revisit(writer, source, identifier="missing", reference=False)
        return [source, first, second, missing]

    docs, report = WarcEvidenceReader().load_archive(archive(tmp_path, build))
    assert len(docs) == 2
    assert [item["reason"] for item in report["omitted_records"]] == ["revisit_source_unavailable"] * 2


def test_missing_digests_are_not_claimed_verified(tmp_path):
    path = archive(tmp_path)
    # Remove declared digests, leaving the content and WARC block lengths intact.
    rows = path.read_bytes().split(b"\r\n")
    path.write_bytes(
        b"\r\n".join(row for row in rows if not row.startswith((b"WARC-Block-Digest:", b"WARC-Payload-Digest:")))
    )
    docs = WarcEvidenceReader().load_data(path)
    assert len(docs) == 1
    assert evidence(docs[0])["digest_verification"] == "not_available"
    assert evidence(docs[0])["payload_digest"] is None


def test_yaml_validation_is_atomic():
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    config = Configer()
    config.value = {"name": "changed", "max_records": "10"}
    reader = WarcEvidenceReader(name="original")
    with pytest.raises(ValueError, match="max_records"):
        reader._initialize_by_component_configer(ComponentConfiger().load_by_configer(config))
    assert reader.name == "original" and reader.max_records == 10000


def test_duplicate_record_id_rejected(tmp_path):
    path = archive(tmp_path, lambda w: [response(w), response(w, b"different")])
    with pytest.raises(ValueError, match="Duplicate WARC"):
        WarcEvidenceReader().load_data(path)


@pytest.mark.parametrize(
    "settings,match",
    [
        ({"max_file_bytes": 10}, "max_file_bytes"),
        ({"max_archive_bytes": 10}, "byte limit"),
        ({"max_records": 1}, "max_records"),
        ({"max_record_bytes": 10}, "max_record_bytes"),
        ({"max_payload_bytes": 10}, "max_payload_bytes"),
        ({"max_text_chars": 5}, "max_text_chars"),
        ({"max_total_chars": 25}, "max_total_chars"),
    ],
)
def test_resource_bounds(tmp_path, settings, match):
    path = archive(tmp_path, lambda w: [response(w), response(w, identifier="two")], compressed=True)
    with pytest.raises(ValueError, match=match):
        WarcEvidenceReader(**settings).load_data(path)


def test_snapshot_identity_reserved_metadata_and_optional_dependency(tmp_path, monkeypatch):
    path = archive(tmp_path, lambda w: [response(w), response(w, identifier="two")])
    ext = {"team": {"names": ["archive"]}}
    docs = WarcEvidenceReader().load_data(path, ext_info=ext)
    docs[0].metadata["team"]["names"].append("changed")
    assert docs[1].metadata["team"] == ext["team"]
    duplicate = tmp_path / "copy.warc"
    shutil.copyfile(path, duplicate)
    assert [doc.id for doc in WarcEvidenceReader().load_data(duplicate)] == [doc.id for doc in docs]
    with pytest.raises(ValueError, match="reserved"):
        WarcEvidenceReader().load_data(path, {"warc_evidence": {}})
    monkeypatch.setitem(sys.modules, "warcio.archiveiterator", None)
    with pytest.raises(ImportError, match="warc_ext"):
        WarcEvidenceReader().load_data(path)


@pytest.mark.parametrize("value", [0, True, "3", 50001])
def test_invalid_settings(tmp_path, value):
    with pytest.raises(ValueError):
        WarcEvidenceReader(max_records=value).load_data(archive(tmp_path))


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

    path = archive(tmp_path)
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
        app.value = {"BASE_INFO": {"appname": "warc-evidence-test"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
        copied = tmp_path / "reader.yaml"
        shutil.copyfile(
            root / "agentuniverse/agent/action/knowledge/reader/file/warc_evidence_reader.yaml.example", copied
        )
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        reader = WarcEvidenceReader().initialize_by_component_configer(config)
        store = SQLiteStore(
            name="warc_store", db_path=str(tmp_path / "knowledge.db"), keyword_extractor="warc_keywords"
        )
        store._new_client()
        components = [
            reader,
            store,
            BaseRouter(name="base_router"),
            JiebaKeywordExtractor(name="warc_keywords", top_k=20),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["warc_store"], readers={"warc": "warc_evidence_reader"})
        knowledge.insert_knowledge(source_path=str(path))
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="alpha")
        assert len(result) == 1 and result[0].text == "alpha archived evidence"
        assert evidence(result[0])["record_id"] == "<urn:test:one>"
        assert evidence(result[0])["archive_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
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


@pytest.mark.parametrize("removed", [1, 2, 3, 4])
def test_missing_final_separator_rejected(tmp_path, removed):
    path = archive(tmp_path)
    path.write_bytes(path.read_bytes()[:-removed])
    with pytest.raises(ValueError, match="separator"):
        WarcEvidenceReader().load_archive(path)


def test_record_offsets_and_extra_separator_rejected(tmp_path):
    path = archive(tmp_path, lambda w: [response(w), response(w, identifier="two")])
    docs, _ = WarcEvidenceReader().load_archive(path)
    first, second = map(evidence, docs)
    assert first["uncompressed_record_offset"] == 0
    assert second["uncompressed_record_offset"] == first["uncompressed_record_length"] + 4
    raw = path.read_bytes()
    offset = second["uncompressed_record_offset"]
    path.write_bytes(raw[:offset] + b"\r\n" + raw[offset:])
    with pytest.raises(ValueError, match="separator"):
        WarcEvidenceReader().load_archive(path)
