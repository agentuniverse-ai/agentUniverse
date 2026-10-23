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
- [default_docx_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/docx_reader.yaml)：读取本地Docx文件中的文本内容
- [default_pdf_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/pdf_reader.yaml)：读取本地Pdf文件中的文本内容
- [default_pptx_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/pptx_reader.yaml)：读取本地Pptx文件中的文本内容
- [default_txt_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/txt_reader.yaml)：读取txt文件中的文本内容
- [default_tsv_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/tsv_reader.yaml)：读取制表符分隔的表格，支持引号内的制表符与多行字段。
- [default_zip_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/zip_reader.yaml)：读取ZIP压缩包文件，支持嵌套ZIP结构和多种文件格式
- [default_web_pdf_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/web_pdf_reader.yaml)：读取本地Docx文件中的文本内容
- [default_markdown_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/markdown_reader.yaml)：读取本地Markdown文件中的文本内容
- [default_rar_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/rar_reader.yaml)：读取 RAR 压缩文件（.rar）中的文本内容。

### TSV 知识文件

`TSVReader` 将制表符分隔的整张表格读取为一个 Document：

```python
from agentuniverse.agent.action.knowledge.reader.file.tsv_reader import TSVReader

documents = TSVReader().load_data(
    file="faq.tsv", ext_info={"collection": "product_faq"}
)
```

支持文件路径、文本流和二进制流。引号包围的字段可以包含制表符或换行符；
若使用单引号包围字段，可指定 `quotechar="'"`。文本规范化、编码检测、
`file_name` 元数据和 `ext_info` 与 `CSVReader` 一致，不关闭调用者传入的流。
直接复用现有 CSV 解析器，不增加依赖。

`FileReader` 自动将 `.tsv` 文件（包括 `.TSV`）交给此 Reader；`ReaderManager`
将文件类型 `tsv` 映射到 YAML 组件 `default_tsv_reader`，可用于常规知识加载流程。
