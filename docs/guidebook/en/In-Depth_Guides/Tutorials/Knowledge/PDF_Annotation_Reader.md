# PDF annotation evidence reader

`PdfAnnotationReader` retrieves PDF reviews independently of ordinary page-text ingestion. It creates one Document per Text, FreeText, Highlight, Underline, Squiggly or StrikeOut annotation, including comments with empty/missing plain text. Install `pip install "agentUniverse[pdf_ext]"`.

```python
from agentuniverse.agent.action.knowledge.reader.file.pdf_annotation_reader import PdfAnnotationReader
documents, report = PdfAnnotationReader().load_annotations("review.pdf")
for document in documents:
    print(document.text, document.metadata["pdf_annotation"])
print(report["omitted_annotations"])
```

Copy `pdf_annotation_reader.yaml.example` to the configured application Reader package as `.yaml`. Explicitly configure Knowledge `readers: {pdf: pdf_annotation_reader}`; this selects review extraction for that Knowledge instance. Ordinary PDF routing is unchanged globally. Use normal `insert_knowledge` / `query_knowledge`; tests exercise YAML → Knowledge → SQLite. `load_data` returns Documents only; inspect omissions with `load_annotations`.

## Evidence and coordinates

Text contains annotation type, one-based page number and plain comment, or an explicit empty-comment marker. Metadata `pdf_annotation` carries file SHA-256, absolute path, page/annotation index, indirect object reference, author/subject/name, raw creation/modification dates, Rect, QuadPoints, flags, page MediaBox/CropBox/rotation/UserUnit and reply relationship. Dates and authors are document claims, not authenticated identity or timestamps. Rich-text presence is recorded but rich text is not interpreted. Metadata is isolated per Document; caller metadata cannot replace the reserved key.

Coordinates remain in **unrotated PDF default user space**, with no conversion to screen pixels. Rect and each eight-number QuadPoints group are different anchors; preserve both. Interpret them with page boxes, rotation and UserUnit (default unit is 1/72 inch). Crop/rotation are not silently applied to the stored numbers. Coordinates do not establish an exact quotation: no page text is extracted or associated with the anchor, and `anchor_text_extracted` is always false. Hidden/no-view annotation flags are retained; this reader does not claim every annotation is visible.

Replies resolve a single exact indirect-object reference against page annotation arrays. Results distinguish resolved, unsupported target, ambiguous repeated target and orphan/direct reference. Cycles are not followed and no thread order is inferred. Annotation `/NM` is not treated as unique. IDs derive from file hash and page/annotation position; byte-identical relocated copies retain IDs. A changed PDF creates a new snapshot; no Store cleanup is performed.

## Limits

Only local unencrypted PDFs. Attachments, actions, links, widgets and other annotation types are not extracted or executed; unsupported types appear in the report. No rendering or appearance-stream extraction happens in production. Encrypted/malformed files and malformed selected coordinates/strings fail. Missing QuadPoints is preserved as null rather than invented. This is not a complete PDF validator or parser sandbox.

Positive integer defaults / maximum settings: `max_file_bytes` 32M/128M, `max_pages` 2,000/10,000, `max_annotations` 20,000/100,000 (includes unsupported types), `max_document_chars` 200,000/2M, `max_total_chars` 10M/40M. M is decimal. Per-document limit also checks selected string metadata. Files are bounded but parsed in memory; page-tree/object-stream parsing can consume more memory than file size, so limits do not guarantee a parser memory or time ceiling. Budget failures return no partial result.

## Verification

Tests export actual two-page PDFs using ReportLab/pypdf, independently inspect comments/replies/QuadPoints with PyMuPDF, and verify rotated/cropped coordinates, empty comments, orphan/ambiguous replies, UserUnit, multi-quads, encrypted files, budgets, source hash preservation and actual SQLite retrieval. A rendered fixture is visually checked with Poppler. PyMuPDF and ReportLab are test-only dependencies, not production imports.

```sh
pip install pypdf==5.9.0 pymupdf==1.26.4 reportlab==4.4.3
python -m pytest -q --import-mode=importlib tests/test_agentuniverse/unit/agent/action/knowledge/reader/test_pdf_annotation_reader.py
```

References: [pypdf annotation reading](https://pypdf.readthedocs.io/en/stable/user/reading-pdf-annotations.html), [PyMuPDF annotation API](https://pymupdf.readthedocs.io/en/latest/annot.html).
