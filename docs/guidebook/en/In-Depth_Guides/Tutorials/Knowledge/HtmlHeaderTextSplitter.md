# HTMLHeaderTextSplitter

A knowledge pre-processing component that splits HTML documents by header hierarchy (`<h1>`–`<h6>`), recording the header path as metadata on each chunk.

## Features

- **Zero dependencies**: Uses Python's built-in `html.parser` — no `beautifulsoup4` or `lxml` required.
- **Header path tracking**: Each chunk carries a `header_path` metadata key (e.g. `"Installation > macOS"`).
- **Hierarchical reset**: When a header at level N appears, all headers at levels >N are cleared.
- **Safe content extraction**: `<script>`, `<style>`, `<noscript>`, `<head>` content is skipped.
- **Configurable**: Custom metadata key name; optionally include or drop text before the first header.

## Configuration

```yaml
name: 'html_header_text_splitter'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.html_header_text_splitter'
  class: 'HtmlHeaderTextSplitter'
header_path_key: 'header_path'
include_unsectioned: true
```

## Usage

```python
from agentuniverse.agent.action.knowledge.doc_processor.html_header_text_splitter import HtmlHeaderTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document

processor = HtmlHeaderTextSplitter()
docs = processor.process_docs([
    Document(text="<h1>Installation</h1><p>brew install x</p><h2>macOS</h2><p>brew</p>"),
])
for doc in docs:
    print(doc.metadata["header_path"], "->", doc.text)
```
