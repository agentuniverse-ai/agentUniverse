# Footnote-aware paragraph ingestion

An ordinary paragraph splitter can separate a claim from its footnote condition.
`FootnoteContextSplitter` keeps contiguous source paragraphs and appends the
definitions referenced by that chunk, so both retrieval and downstream readers
see the condition. This is opt-in ingestion, not a citation detector or truth judge.

```python
from agentuniverse.agent.action.knowledge.doc_processor.footnote_context_splitter import FootnoteContextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document

source = Document(text="Voltage 12 V[^v].\n\nOther section.\n\n[^v]: At 20°C only.",
                  metadata={"source": "manual-v1"})
chunks = FootnoteContextSplitter(chunk_chars=25).process_docs([source])
assert "At 20°C only" in chunks[0].text
```

## Pipeline configuration

Register the supplied `footnote_context_splitter.yaml` as a DOC_PROCESSOR. Use
`insert_processors: [footnote_context_splitter]` on Knowledge and register a
`TxtReader` named `raw_text`, with `readers: {md: raw_text}`. The default Markdown
reader may remove markup, so it is not appropriate for this processor. Configure
`source_key: file_name` for TxtReader when filenames are unique in the corpus.
For corpora with duplicate basenames use a source-aware Reader that supplies a
stable unique `source` metadata value. The current public Knowledge loader does
not forward call-time `ext_info` into Reader.load_data; passing it to
`insert_knowledge` does not establish source identity. By default `source` is used, falling back to
the input Document ID; identical content with identical IDs needs distinct source
metadata to avoid sharing output IDs. Complete documents, not pre-split pages,
must reach this processor. Do not apply a later splitter that detaches the notes.

## Explicit input grammar

This is a bounded Markdown-footnote subset, not a full Markdown renderer:

- References are `[^label]`, labels are case-sensitive ASCII letters, digits,
  underscore or hyphen, length 1–64. No numeric/superscript or PDF-layout guessing.
- Definitions start a line with at most three spaces followed by `[^label]:`.
  Four-space/tab-indented continuation lines, including blank-separated indented
  paragraphs, remain part of the definition. All original indentation is retained.
- Fenced backtick/tilde code, indented code and matched equal-length backtick code
  spans do not produce references/definitions. Backslash-escaped markers are literal.
  Inline spans may cross lines but not blank paragraphs or excluded blocks.
- HTML, block-quoted/list-contained definitions, Unicode labels, renderer-specific
  label normalization and nested footnote expansion are not supported. References
  inside definitions are not recursively followed. Pre-normalize those formats
  with a source-aware reader instead of assuming general Markdown compatibility.

Duplicate supported definitions raise, including identical duplicates. Unknown
labels are reported in `unresolved`, or raise with `missing: error`; no definition
is invented. Each input document is an isolated namespace. Unreferenced definitions
are preserved in original source chunks. A definition already fully in the body
chunk is not copied again; remote definitions are appended once per label in first
reference order. Appending can increase keyword recall as well as output size.

## Evidence and resource contracts

Every output has `metadata.footnote_context`: source identity, parent ID, SHA-256
of original text, contiguous `[start,end)` source span, reference spans, resolved
definition source/output spans, unresolved labels and an over-target flag. Offsets
count Python Unicode code points, end-exclusive; they refer to reader output, not
byte positions in the original file. Appended separators are two newlines. Original
source spans partition the complete input without dropping characters. Definitions
are copied exactly, including CRLF when present in the input Document.

IDs depend on source identity, parent ID, source digest, span and resulting text.
Input objects/metadata are not mutated; output metadata is deep-copied. Embeddings
and keywords are cleared because chunk content changed. Reprocessing outputs raises
on the reserved `footnote_context` field instead of nesting stale offsets.

`chunk_chars` (1500) is a **soft character target**, not a token limit. Atomic
paragraphs, definitions and fenced blocks may exceed it, and attached notes can
also exceed it; `over_chunk_target` reports this. Hard limits reject, not truncate:
`max_document_chars` (1,000,000) per input, `max_references` (10,000) per input and
`max_output_chars` (4,000,000) over the whole batch. Bounds concern text, not arbitrary
metadata memory. No files, network calls or executors are opened by the processor.

## 中文

本组件解决“正文被召回，但限定条件留在远处脚注”的问题。它按显式 Markdown
脚注标签关联原文定义，切分后携带所需脚注并保留精确来源位置，不猜测 PDF 页脚。
重复定义报错、缺失定义显式报告；没有引用的定义也不会丢失。段落目标是软字符
预算，输出总量另有硬上限。必须传入完整、保留标记的文本，且不要再使用会拆散
脚注的后置切分器。此能力不证明引用真实、内容正确或检索准确率提高。

Tests cover exact CRLF/Unicode spans, multiline notes, code/escaped markers,
source isolation, limits and real YAML/manager registration. A real Markdown file
passes through public Knowledge insertion into SQLite, close/reopen and query,
with only tracing mocked. This is functional evidence, not a production benchmark.
