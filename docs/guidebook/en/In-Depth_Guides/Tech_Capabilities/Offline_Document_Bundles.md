# Verified offline Document bundles

Export selected Documents and explicitly supplied UTF-8 source texts to a portable `.auc` file. Import verifies the complete bundle before returning Documents; it never extracts files or writes to a Store.

```python
from agentuniverse.agent.action.knowledge.corpus_bundle import export_bundle, load_bundle
from agentuniverse.agent.action.knowledge.store.document import Document

sha = export_bundle(
    "research.auc", [Document(id="chunk-1", text="Evidence text")],
    sources={"paper-1": "Evidence text"},
    document_sources={"chunk-1": ["paper-1"]},
)
documents = load_bundle("research.auc", expected_sha256=sha)
```

Destination parent must already exist. Export uses a flushed temporary file and atomic no-clobber hard-link publication. Existing files are never replaced. Filesystems without hard-link support fail explicitly; temporary files are cleaned on ordinary failures. This is not a power-loss durability guarantee for the parent directory.

Default export omits embeddings and **all metadata**. Explicit `metadata_keys=["page"]` opts in selected top-level keys; values must round-trip losslessly through JSON. Document text, source text, IDs and keywords are still content: select and review them before export. This is not encryption or automatic secret detection.

For Knowledge, copy `reader/file/corpus_bundle_reader.yaml.example` to your application's component directory and configure `readers: {auc: corpus_bundle_reader}`. Call `knowledge.insert_knowledge(source_path="research.auc")`. The adapter validates every member before the existing insert pipeline begins; a damaged last member cannot insert earlier documents. Store write failures and cross-store transactions retain existing Knowledge semantics. To pin an externally retained digest, set the Reader's `expected_sha256`. Limits (`max_bytes`, `max_documents`, `max_sources`) are configurable in YAML.

Version 1 is an unencrypted, **uncompressed** ZIP with exactly these members:

- `manifest.json`: object with `format="agentuniverse-document-bundle"`, integer `version=1`, `sources` and `documents` arrays.
- `sources/N.txt`: UTF-8 source text. Corresponding manifest row has `id`, `member`, `sha256`.
- `documents/N.json`: object with `id`, `text`, plain JSON `metadata`, string-array `keywords`. Corresponding manifest row has `id`, `member`, `sha256`, and nonempty unique source-ID array `sources`.

Indices are zero based within each array. Hashes are lowercase SHA-256 of exact member bytes. IDs are stable logical identifiers, not filesystem locations. Unknown fields/versions, duplicate IDs/JSON keys/ZIP members, missing/extra members, noncanonical paths, inconsistent IDs, nonfinite JSON and malformed references fail validation. Source associations are caller assertions; the format does not prove chunks were derived from sources or that the sources are true. Internal hashes detect corruption, not malicious replacement; retain the returned whole-archive hash separately or use a separate trusted signing/distribution mechanism.

Loaded Documents get reserved `_corpus_bundle` metadata with archive/document hashes, source IDs/hashes and format version. Vectors are empty. No user-supplied `_corpus_bundle` metadata is accepted. File count, archive and uncompressed byte counts are bounded; the full bounded archive is held in memory. This is a portable interchange format, not a Store snapshot, full metadata backup, remote URL loader, incremental sync or authenticated archive.

Tests use actual ZIP files, an independently authored V1 package, cross-directory rename, corruption/rehashed invalid payloads, unsupported compression/version, duplicate entries, concurrent destination publication, failure cleanup and real YAML→Reader→Knowledge→SQLite retrieval. The integration verifies the database remains empty after a late-member validation failure.
