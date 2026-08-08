# HTMLHeaderTextSplitter

知识预处理组件，按 HTML 标题层级（`<h1>`–`<h6>`）切分文档，将标题路径记录到每个块的 metadata 中。

## 特点

- **零依赖**：使用 Python 内置 `html.parser`，无需安装 `beautifulsoup4` 或 `lxml`。
- **标题路径追踪**：每个块携带 `header_path` metadata 键（如 `"安装 > macOS"`）。
- **层级重置**：出现 N 级标题时，所有 >N 级的标题被清除。
- **安全内容提取**：跳过 `<script>`、`<style>`、`<noscript>`、`<head>` 内容。
- **可配置**：自定义 metadata 键名；可选是否保留第一个标题前的文本。

## 配置

```yaml
name: 'html_header_text_splitter'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.html_header_text_splitter'
  class: 'HtmlHeaderTextSplitter'
header_path_key: 'header_path'
include_unsectioned: true
```

## 使用示例

```python
from agentuniverse.agent.action.knowledge.doc_processor.html_header_text_splitter import HtmlHeaderTextSplitter
from agentuniverse.agent.action.knowledge.store.document import Document

processor = HtmlHeaderTextSplitter()
docs = processor.process_docs([
    Document(text="<h1>安装</h1><p>brew install x</p><h2>macOS</h2><p>brew</p>"),
])
for doc in docs:
    print(doc.metadata["header_path"], "->", doc.text)
```
