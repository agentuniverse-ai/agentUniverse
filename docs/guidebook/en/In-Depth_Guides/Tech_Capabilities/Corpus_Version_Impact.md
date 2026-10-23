# Corpus version impact reports

Compare two explicitly supplied, verified source snapshots before reviewing stored citations. This read-only API has no dependency on the offline bundle format or any Store.

```python
from agentuniverse.agent.action.knowledge.corpus_impact import source_record, compare_corpora

before = {"version": 1, "sources": [source_record("manual", "First\nOld\n", location="old.txt")]}
after = {"version": 1, "sources": [source_record("manual", "First\nNew\n", location="new.txt")]}
report = compare_corpora(before, after, [
    {"id": "answer-42-citation", "source_id": "manual", "start_line": 2, "end_line": 2}
])
```

`source_record` accepts explicit UTF-8 source text, a stable logical ID, an optional location label, and optional `{id, text}` chunks. Existing Documents can supply `{"id": doc.id, "text": doc.text}`. It records exact SHA-256 hashes. A V1 manifest has only `version` and `sources`; each source has `id`, `text`, `sha256`, `location`, `chunks`; each chunk has `id`, `text`, `sha256`. The comparator verifies **both complete manifests**, rejects duplicate source/chunk IDs, unknown fields, wrong digests and unsupported versions before comparing. Chunk/source association remains a caller assertion.

Reports distinguish source additions/removals, exact original-text changes, location changes and chunk-ID/content changes. Rechunking alone does not mark source text as changed. IDs establish identity; a changed location with the same ID is a location change. Equal content hashes across removed/added IDs produce only `possible_identity_matches`, because repeated boilerplate is common.

References require unique `id` and `source_id`, with optional `chunk_id` and paired one-based inclusive `start_line`/`end_line` in the OLD text. Missing old targets are `unresolved`. Removed/changed source/chunk targets are `affected`. An unchanged line anchor in a changed source is still affected for review: unchanged text does not prove semantic validity in new context. Line mapping distinguishes `anchor_changed`, `anchor_shifted`, `anchor_unchanged` and budget-unavailable mapping. Duplicate lines may have multiple valid alignments; the deterministic SequenceMatcher alignment is evidence, not authoritative provenance.

`line_diff` uses zero-based half-open ranges and operations insert/delete/replace, retaining newline differences. No raw source or chunk text is included in the report. Source count, total UTF-8 text bytes, chunks, references and line-pair work are bounded. Exceeding the line-diff budget explicitly omits line mapping while retaining hash-based impact. Core input limits raise ValueError. Caller-supplied limits can raise the cost.

CLI for local JSON files:

```sh
python -m agentuniverse.agent.action.knowledge.corpus_impact old.json new.json --references references.json
```

The CLI rejects duplicate JSON keys and limits each input file to 32 MiB. It prints deterministic JSON and never updates its inputs or a Store. Internal digests verify content consistency, not origin/authenticity. No fuzzy semantic matching, automatic repair, Store synchronization, or claim that a citation remains correct is made.
