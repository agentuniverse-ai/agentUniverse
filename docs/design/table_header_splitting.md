# Header-preserving table splitting / 保留表头的表格拆分

`TableHeaderSplitter` is an optional insertion DocProcessor for raw Markdown
pipe tables. It repeats each table's **original** header and alignment row in
every row-group chunk. It also repeats the original ATX heading hierarchy and
nearest plain paragraph (often a caption or unit statement). It never invents
units or column meanings. The source prose remains as separate chunks.

## Configuration and real file ingestion

The default MarkdownReader uses an unstructured loader that may remove pipe
markup. Select the existing raw `TxtReader` explicitly; do not use LineTxtReader,
which separates the header from the data before this processor can see them.
Register these reader options in a component YAML:

```yaml
name: raw_markdown
description: Preserve Markdown table syntax as raw text.
metadata:
  type: READER
  module: agentuniverse.agent.action.knowledge.reader.file.txt_reader
  class: TxtReader
```

Add to the Knowledge YAML (other store settings remain your own):

```yaml
readers:
  md: raw_markdown
insert_processors:
  - table_header_splitter
```

The shipped processor YAML uses `max_chars: 2000`. This is a **soft character
budget for table chunks**, counting repeated context and headers. It is not a
token budget and does not split ordinary prose. Rows are indivisible: a row
that cannot fit with its header/context is emitted alone with `over_budget: true`.
Header-only tables are also retained and can exceed the budget. No row is dropped.
Avoid a generic splitter after this component if it would detach the repeated
headers again. A downstream context compressor may truncate a table; applications
requiring complete rows must choose an appropriate final context policy.

## Supported grammar and conservative behavior

- At least two columns, optional outer pipes, up to three leading spaces.
- Alignment cells match `:?-{3,}:?`; header and data rows have equal column counts.
- Backslash-escaped pipes stay in cells; an even number of preceding backslashes
  leaves a pipe as a delimiter. Original row/cell text is not rewritten.
- Backtick/tilde fences and indented code are not parsed as tables. Matching
  closing fences must use the same character and at least the opening length.
- Uneven multi-column rows make that candidate block remain verbatim. A line
  without a multi-column pipe row terminates the table, becoming ordinary prose.
- LF and CRLF are preserved at the Document-text level; TxtReader itself uses
  Python's universal-newline reading, so file-byte offsets are not promised.
- No HTML/XLSX merged cells, blockquote/list-nested tables, multiline cells,
  setext heading inference or full CommonMark/GFM conformance. Pipes in inline
  code must be escaped too. These unsupported formats are not repaired.

The nearest plain paragraph is retained verbatim, not classified as a caption.
Blank lines may separate it from the table. Headings, pipe rows, fences and
indented code delimit this paragraph. Very large headers/context can themselves
exceed the budget; the `over_budget` flag makes that explicit.

## Metadata, identity and compatibility

New chunks have a reserved `metadata.table_chunk` object. Table chunks contain
`kind: table`, stable `table_id`, `source_document_id`, original `header_text`,
`heading_context`, `preceding_context`, and `over_budget`. `row_start`/`row_end`
are **zero-based half-open data-row ranges**, excluding the header; a header-only
table uses [0,0). `source_start`/`source_end` identify that chunk's original data
rows in Python string-character offsets; `table_start`/`table_end` cover the whole
source table. Repeated context is recorded separately, not falsely included in
the contiguous data-row range. Prose chunks have `kind: prose` and their own
exact source offsets.

IDs include parent document ID, source identity and offsets. Use a unique parent
ID or `metadata.source` per origin. In its absence `file_name` is used; basename
alone cannot distinguish equal files in different directories. Different source
IDs with identical content, and repeated identical tables at different offsets,
remain distinct. IDs are stable on repeated runs with the same content/config.

Input objects/metadata are unchanged. New top-level dictionaries are made;
nested input metadata remains shared. New chunks clear embeddings and keywords
because the text has changed; subsequent embedding/extraction stages should
compute them afresh. If no supported table exists the original document is
returned unchanged. An existing reserved `table_chunk` on a document containing
a recognized table raises rather than overwriting user data/re-splitting silently.
Without configuring this processor, Knowledge's existing insertion is unchanged.

## Validation / 验证范围

Run the complete offline workflow from the repository root in a fresh process:

```shell
python -m examples.table_header_sqlite_demo
```

It loads the shipped splitter YAML with max_chars120, writes a synthetic
12-row parameter table to a temporary Markdown file, registers actual components,
and invokes public Knowledge insertion through TxtReader. After closing and
reopening SQLite, public query results include repeated column names/units,
file provenance and row ranges. Managers, router, tracing and SQL are not mocked.
JSON output permits checking that all12 rows appear exactly once. Keyword
extraction and recall limits are explicitly raised to100 for this small fixture;
this does not claim production recall quality. Threads/connections are closed
and only the example's temporary directory is removed. No API or server needed.

Tests check exact row reconstruction, unit-bearing headers and caption context,
both newline styles, soft-budget overflow, escapes, fences, Unicode, unsupported
tables, source-aware stable IDs, no mutation, YAML discovery and invalid options.
Integration uses an actual `.md` file, `TxtReader`, public `insert_knowledge`, a
SQLite database closed/reopened, and public `query_knowledge`. Only managers,
the routing choice and tracing are mocked. No external model or API is required.

A separate test scans the real processor package, discovers the shipped YAML,
invokes the framework bootstrap registration method and retrieves it through
the actual manager. It checks default configuration, a250-row table split with
all rows accounted for and unit-bearing headers repeated, and isolation of
fetched configuration copies. Only singleton state is isolated for this test;
it does not start a complete application server or prove retrieval quality.

本组件用于原始 Markdown 管道表格，不解析任意 Excel/HTML 表格。每块重复原表头、
标题层级及紧邻说明段落，保留列名和原有单位；不推测单位。预算为字符软上限，
超长单行不截断、不丢弃，而是标记超限。元数据提供行号区间、来源及原文字符偏移，
可核验原始数据行恰好出现一次（表头和上下文按设计重复）。入库必须为 `.md`
配置原始全文 TxtReader。测试覆盖真实文件到存储再召回，不代表完整应用启动、
所有 Markdown 语法兼容或生产检索效果已验证。
