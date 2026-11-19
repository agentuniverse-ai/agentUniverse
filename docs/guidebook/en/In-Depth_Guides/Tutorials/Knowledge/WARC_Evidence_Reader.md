# WARC evidence reader

`WarcEvidenceReader` extracts archived HTTP text from local `.warc` and `.warc.gz` files without requesting their URLs. Install `pip install "agentUniverse[warc_ext]"`.

```python
from agentuniverse.agent.action.knowledge.reader.file.warc_evidence_reader import WarcEvidenceReader

documents, report = WarcEvidenceReader().load_archive("snapshot.warc.gz")
for document in documents:
    print(document.metadata["warc_evidence"], document.text)
print(report["omitted_records"])
```

Copy `warc_evidence_reader.yaml.example` into your configured Reader package as `.yaml`. In Knowledge configuration use `readers: {warc: warc_evidence_reader}`. The normal `insert_knowledge(source_path=...)` and `query_knowledge(...)` path is covered with real SQLite. Knowledge routes by the final extension: compressed files require an explicit `gz` mapping, which also routes other `.gz` files to this reader and may reject them. Direct `load_archive` avoids that ambiguity. `load_data` returns only Documents; use `load_archive` to inspect omissions.

## Evidence

Each response is a separate Document. Reserved metadata `warc_evidence` includes the archive SHA-256, original record ID/type/target URI/capture date, supplied digests and verification status, decoded payload and text hashes, and byte offset/length in the **decompressed** WARC (length excludes the four-byte separator). Date and URL are archive claims, not independent authenticity evidence. IDs use archive digest and record ID, so byte-identical relocated files retain IDs. Repacking an archive produces a new snapshot. No Store synchronization/deletion is performed.

Supported: WARC 1.0/1.1, full 2xx HTTP responses with text/plain, text/html or application/xhtml+xml, strict declared charset (UTF-8 default), identity/chunked transfer and identity/gzip content encoding. HTML uses BeautifulSoup text extraction, removes script/style/template, and is labelled derived text. Cookies and arbitrary request/response headers are not copied. Missing digest is explicitly unverified; a hash is not proof of origin.

Revisits resolve only the identical-payload profile, by exact `WARC-Refers-To` ID in the same archive and matching verified source payload digest. Reference date/URL, when present, must agree. No URL guessing, chain following, network fallback or invented payload. Unsupported type/profile, missing source, non-success/partial HTTP responses, unsupported media/encoding, truncated/segmented records appear in `omitted_records`. A revisit document keeps its own capture date and separately records the source capture date.

Malformed lengths/digests, duplicate IDs, missing/extra CRLF separators, undecodable selected text and exhausted budgets fail without returning partial Documents. This is a deliberately restricted reader, not a complete WARC conformance validator. Chunk trailers are unsupported. The original file is never modified.

## Resource limits

All options are positive integer byte/count/character limits; booleans are rejected. Defaults (and hard configuration ceilings): `max_file_bytes` 32M (128M), `max_archive_bytes` 128M (256M), `max_records` 10,000 (50,000), `max_record_bytes` and `max_payload_bytes` 8M (32M), `max_text_chars` 2M (8M), `max_total_chars` 10M (40M). Limits use decimal units. Archives are bounded but buffered in memory, not streamed from disk. HTML parser memory/latency is not guaranteed by these limits. Caller metadata is deep-copied and cannot replace `warc_evidence`.

## Verification

Tests use real warcio 1.7.5 WARCWriter files (1.0/1.1, gzip), HTTP gzip/chunking, digest failures, revisit relationships and budget boundaries. Integration captures a controlled loopback HTTP server through warcio and compares independent expected text; no public site or paid model is used. The unit suite includes YAML → Knowledge → SQLite retrieval. Run both reader test modules plus Knowledge regression tests:

```sh
python -m pytest -q --import-mode=importlib tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_warc_evidence_reader.py tests/test_agentuniverse/integration/test_warc_evidence_capture.py
```

References: [WARC specifications](https://iipc.github.io/warc-specifications/) and [warcio](https://github.com/webrecorder/warcio).
