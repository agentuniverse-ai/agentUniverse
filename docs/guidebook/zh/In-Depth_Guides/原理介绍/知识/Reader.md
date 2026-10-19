# Reader

Reader负责从各式各样的信息源中将信息抽取成agentUniverse中的Document形式。这些信息源可以是各种本地文件，也可以是网页或者一个IO接口，

Reader的定义如下:
```python
from abc import abstractmethod
from typing import List, Any, Optional

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase

class Reader(ComponentBase):
    """The basic class for the knowledge reader."""
    component_type: ComponentEnum = ComponentEnum.READER
    name: Optional[str] = None
    description: Optional[str] = None

    def load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the input params."""
        return self._load_data(*args, **kwargs)

    @abstractmethod
    def _load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the input params."""
```
用户在自定义的Reader子类中，需要重写`_load_data`函数，读取数据并输出List[Document]。

在编写完对应代码后，可以参考下面的yaml将你的Reader注册为aU组件：
```yaml
name: 'default_txt_reader'
description: 'default txt reader'
metadata:
  type: 'READER'
  module: 'agentuniverse.agent.action.knowledge.reader.file.txt_reader'
  class: 'TxtReader'
```
其中metadata的type固定为READER

### 关注您定义的Reader所在的包路径
在agentUniverse项目的config.toml中需要配置Reader配置对应的package, 请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`reader`路径或其子路径下。

以示例工程中的配置为例，如下：
```yaml
[CORE_PACKAGE]
reader = ['sample_standard_app.intelligence.agentic.knowledge.reader']
```

## agentUniverse目前内置有以下Reader:
- `default_jsonl_reader`：读取 UTF-8 编码的 JSON Lines（`.jsonl`）与 NDJSON（`.ndjson`）文件，每个非空行生成一个 Document。
- [default_docx_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/docx_reader.yaml)：读取本地Docx文件中的文本内容
- [default_pdf_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/pdf_reader.yaml)：读取本地Pdf文件中的文本内容
- [default_pptx_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/pptx_reader.yaml)：读取本地Pptx文件中的文本内容
- [default_txt_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/txt_reader.yaml)：读取txt文件中的文本内容
- [default_zip_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/zip_reader.yaml)：读取ZIP压缩包文件，支持嵌套ZIP结构和多种文件格式
- [default_web_pdf_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/web_pdf_reader.yaml)：读取本地Docx文件中的文本内容
- [default_markdown_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/markdown_reader.yaml)：读取本地Markdown文件中的文本内容
- [default_rar_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/rar_reader.yaml)：读取 RAR 压缩文件（.rar）中的文本内容。

### JSON Lines 知识文件

对于每行一个 JSON 值的语料，可以直接使用 `JsonlReader`：

```python
from agentuniverse.agent.action.knowledge.reader.file.jsonl_reader import JsonlReader

documents = JsonlReader().load_data(
    file="corpus.jsonl", ext_info={"collection": "product_faq"}
)
```

例如，第 1 行为 `{"question": "如何开始？"}`、第 2 行为
`{"question": "如何重置？"}` 的文件会生成两个文档。每个文档的文本是
原始 JSON（去除首尾空白），元数据包含 `file_name`、`file_path`、从 1 开始的实际 `line_number`，以及
`json_type`（`object`、`array` 或 `primitive`）。`ext_info` 会复制到每个文档的
元数据中，同名键覆盖自动生成的值。
保留原始文本可避免数值精度和 JSON 转义序列发生变化。

文件必须使用无 BOM 的 UTF-8 编码。空白行被跳过，但实际行号保留；支持 CRLF
换行与末行没有换行符。空文件返回 `[]`。JSON 格式错误（包括 `NaN`、`Infinity`）
抛出包含文件路径和错误行号的 `ValueError`，不会返回部分结果；UTF-8 解码失败
抛出 `UnicodeDecodeError`。

`FileReader` 支持这两种扩展名，`ReaderManager` 将 `jsonl`、`ndjson` 文件类型映射到
YAML 组件 `default_jsonl_reader`。源文件按行读取，但返回的列表仍保存全部文档。
