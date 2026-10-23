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
- [default_zip_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/zip_reader.yaml)：读取ZIP压缩包文件，支持嵌套ZIP结构和多种文件格式
- [default_web_pdf_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/web_pdf_reader.yaml)：读取本地Docx文件中的文本内容
- [default_markdown_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/markdown_reader.yaml)：读取本地Markdown文件中的文本内容
- [default_audio_transcription_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/audio_transcription_reader.yaml)：使用**本地** Whisper 模型（可选 `faster-whisper` 后端，`pip install 'agentuniverse[audio_ext]'`）把本地音频文件（.wav/.mp3/.m4a/.flac/.ogg）转写为文本——无需云端语音 API、无需凭据、音频不出本机。模型按 (model_size, device, compute_type) 在类级缓存；检测到的语言、时长与分段数写入 metadata；`max_file_bytes` 与 `max_duration_seconds` 上限在转写开始前拒绝超大/超长输入。
- [default_rar_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/rar_reader.yaml)：读取 RAR 压缩文件（.rar）中的文本内容。