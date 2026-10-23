# Notebook evidence reader

`NotebookEvidenceReader` turns a **local** `.ipynb` into individually addressable cell sources and, only when requested, cached text outputs. Use it to retrieve experiment explanations/code without silently presenting stored output as a fresh computation. It never starts a kernel, renders HTML, opens links, or decodes attachments.

This is an opt-in Reader, not a notebook linter or execution service. No default extension routing changes. Install the optional validator:

```sh
pip install 'agentUniverse[notebook_ext]'
```

## Direct use

```python
from agentuniverse.agent.action.knowledge.reader.file.notebook_evidence_reader import NotebookEvidenceReader

reader = NotebookEvidenceReader()  # source only, including empty and raw cells
documents, report = reader.load_notebook(
    "experiment.ipynb", notebook_id="research/project-a/experiment-7"
)
for document in documents:
    evidence = document.metadata["notebook_evidence"]
    print(evidence["cell_index"], evidence["json_pointer"], document.text)
print(report["omitted_outputs"])

# Explicitly include stream and text/plain representations, still unverified.
reader = NotebookEvidenceReader(include_text_outputs=True)
documents = reader.load_data("experiment.ipynb")
```

Output Documents are separate from their cell's source. Their text starts with an unverified-cache warning and their metadata links to `source_document_id`. `include_error_outputs=True` independently includes saved error name/value/traceback; the default excludes these because they can contain private data. Opting into text output can also expose private data; it is not a redaction feature.

## Register through YAML and Knowledge

Copy `notebook_evidence_reader.yaml.example` from the reader package into the application's configured Reader package, rename it to `.yaml`, and retain its `metadata` class/module entries. Set the corresponding mapping in your Knowledge configuration:

```yaml
readers:
  ipynb: notebook_evidence_reader
```

Then use the normal `knowledge.insert_knowledge(source_path="experiment.ipynb")` and `query_knowledge(...)` flow. A source-only YAML → Reader → Knowledge → SQLite query is exercised in the tests. To supply a portable namespace directly, call `reader.load_data(..., notebook_id=...)` and pass those Documents to your configured ingestion workflow; ordinary file routing uses the absolute file URI.

## Evidence and identity

- Supports nbformat **4.0–4.5**, validated by `nbformat`. Other versions fail explicitly; no upgrade, normalization, or ID repair is performed. Duplicate/missing/invalid 4.5 IDs are rejected before validation.
- One source Document per cell, in **file order**, with exact normalized source text. List-of-string fields are joined without inserting characters. Execution counts are recorded, not interpreted as chronology, freshness, correctness, or successful execution.
- Metadata includes file SHA-256, namespace, cell ID/index/key, JSON pointer, cell type, language, execution count, text hash and `execution_verified=False`. Metadata is isolated per Document; caller metadata cannot replace the reserved `notebook_evidence` key.
- IDs include namespace **and raw file digest**, plus cell key and source/output ordinal. Re-reading the same snapshot is deterministic; any file-byte change intentionally creates a new snapshot. Pass the same `notebook_id` to retain IDs across relocated byte-identical copies. Without it, absolute paths distinguish files. Pre-4.5 cells use positional keys, not invented stable IDs. Remove obsolete snapshots explicitly through your Store lifecycle; this Reader does not implement synchronization or deletion.
- Selected stream payloads and `text/plain` representations remain text. HTML, images, widgets, JSON bundles and attachments are not rendered/extracted. Available MIME types and attachment names are retained; the report identifies omitted outputs. Raw-cell source remains literal text, with its declared format recorded.
- A notebook's `trusted` metadata is not proof that outputs match its current source. Even the real-kernel integration fixture is marked unverified by this Reader. Error traceback text may contain terminal escape characters and is not sanitized for terminal rendering.

## Bounds and failure behavior

| Setting | Default | Maximum accepted setting |
| --- | ---: | ---: |
| `max_file_bytes` | 20,000,000 | 100,000,000 |
| `max_cells` | 5,000 | 50,000 |
| `max_outputs` (including excluded outputs) | 10,000 | 100,000 |
| `max_source_chars` per cell | 200,000 | 2,000,000 |
| `max_output_chars` per selected payload | 200,000 | 2,000,000 |
| `max_total_chars` including warning labels | 2,000,000 | 20,000,000 |

All limits are positive integers, not booleans/strings. Oversized, invalid-schema, duplicate-key, non-finite-number or unreadable input fails the read with no partial result returned. No silent truncation. The bounded JSON file is parsed in memory; this is not a streaming parser or a sandbox for untrusted documents. Arbitrary notebook metadata is not copied into Documents. Resource bounds do not guarantee a fixed validation latency.

## Verification

The unit suite covers all six supported minors, IDs/snapshots, output selection, raw/empty cells, limits, invalid settings, metadata isolation, and 60 seeded notebooks compared with `nbformat`'s normalized text. A separate integration fixture uses `nbclient` and a private temporary `ipykernel` spec to produce real outputs, then verifies read-only extraction. **Only that explicitly controlled test executes code**; the Reader does not import the execution stack. No model API is used.

```sh
pip install nbformat==5.10.4 nbclient==0.10.2 ipykernel==6.29.5
python -m pytest -q --import-mode=importlib \
  tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_notebook_evidence_reader.py \
  tests/test_agentuniverse/integration/test_notebook_evidence_kernel.py
```

See the [Jupyter format specification](https://nbformat.readthedocs.io/en/latest/format_description.html) and [nbformat API](https://nbformat.readthedocs.io/en/latest/api.html) for schema and string normalization details. This feature does not claim higher retrieval accuracy or verify scientific conclusions.
