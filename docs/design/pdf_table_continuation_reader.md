# Opt-in ruled PDF table reader

The ordinary PDF reader emits page text. A row on a subsequent page may then be
retrieved without the first page's column names. This reader instead emits JSON
table documents, with explicit page/geometry provenance. It does not replace the
ordinary reader or preserve prose, images, footnotes or tables without ruled lines.
Use a separate ordinary PDF ingestion pipeline if that content is required.

Install `agentUniverse[pdf_table_ext]`, register the shipped
`reader/file/pdf_table_reader.yaml` using the normal component bootstrap, then
select `readers: {pdf: pdf_table_continuation_reader}` in Knowledge configuration.
No default reader mapping changes. The optional dependency is pdfplumber 0.11.7+;
the existing `pdf_ext` extra remains unchanged.

## Continuation contract

This is conservative syntactic detection, not a semantic table-understanding model:

- A caption immediately above each ruled table starts with literal `Table` and an
  ASCII identifier of at most 32 letters/digits/dots/underscores/hyphens. Prefix and
  continuation marker are configurable literals; identifier equality is exact.
- The next caption contains the whole literal `continued` marker, matched without
  case. It must refer to the same identifier. A matching marker is an explicit
  document convention, not proof of author intent (negation is not interpreted).
- Pages are physically adjacent; the previous table is last on its page and the
  next table is first. Their edges must be within 84 points of bottom/top.
- All headers are nonempty, with at least two cells, and match after whitespace
  normalization. The first extracted row is assumed to be a header, not inferred.
- Page width and corresponding column boundaries agree within 3 points. Merged
  or ragged cell geometry disqualifies joining. No missing cell values are filled.

Any failed condition leaves tables separate. Matching headers alone never merge
tables. Joining removes only the next segment's repeated first row. The exact
extracted header of every segment remains in metadata. Table data remains strings
or nulls as extracted; there is no numeric/unit/date coercion or OCR.

## Output and identity

Each Document text is JSON `{"header": [...], "rows": [[...], ...]}`. Metadata
contains file URI/name/SHA-256, `pdf_header_assumption: first_extracted_row`, and
`pdf_table_segments` with physical 1-based page numbers, bounding boxes in PDF
points measured from the top, captions, original headers and half-open data-row
ranges. Table indexes are zero-based in page position order. These are extraction
coordinates, not verified textual citations or semantic facts.

IDs hash source URI, file digest and constituent table locations. Re-reading the
same file at the same path is stable; moving/changing the file changes IDs. This
reader does not delete previously ingested versions. Direct `load_data` supports
copied custom metadata but rejects overriding provenance. The current public
Knowledge insert entry point does not forward arbitrary `ext_info` to readers.

## Bounds and failures

Local paths only; one bounded immutable byte snapshot is read. Defaults: 32 MiB,
50 pages, 200 tables, 100,000 extracted cells, 50,000 characters and 20,000 edges
per page, 10 million output characters including serialized metadata. Limits are
positive integers; geometry settings are finite and bounded. Invalid configuration,
corrupt/encrypted unsupported PDFs, extraction errors or exceeded limits fail the
read without returning a partial list. Pages and streams close on failure.

Parser objects, page lists and geometry are allocated before some checks. These
limits are not a parser memory sandbox or wall-clock deadline. Process isolation
and external resource limits are appropriate for untrusted large/complex PDFs.
No network fetches or password management are provided.

## Reproducible verification

Tests require reportlab 4.4.0 (fixture generation), pdfplumber 0.11.7 and pypdf
for adjacent ordinary-reader regressions. `docs/examples/pdf_table_fixture.py`
generates a deterministic two-page fixture and refuses to overwrite an existing
file. Render its pages with Poppler to check layout; tests independently inspect
the extracted cells, not rendered screenshots alone.

The integration test registers the shipped YAML with real Reader/Store/processor/
router managers, ingests the generated PDF through `Knowledge.insert_knowledge`,
reopens an actual SQLite store, and queries a second-page token to recover all
five rows plus both page references. Only tracing side effects are patched. This
demonstrates the specified ruled-table convention, not general financial-report
accuracy, arbitrary PDF layout support or an expected competition score.

The integration explicitly configures Jieba `top_k=100`: the default of 3 does not
index the sample's second-page token. A separate case verifies this limitation
while confirming that the stored table still contains that row. Extraction alone
does not guarantee recall; select a suitable keyword budget or vector store for
your data. No global keyword defaults are changed by this reader.
