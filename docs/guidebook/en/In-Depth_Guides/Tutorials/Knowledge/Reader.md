# Reader

The Reader is responsible for extracting information from various sources into the Document format used within agentUniverse. These sources can range from local files to web pages or even an I/O interface.

The Reader is defined as follows:
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
When creating a custom subclass of Reader, you need to override the `_load_data` function, which is responsible for reading data and outputting a List[Document].

After writing the corresponding code, you can refer to the following YAML configuration to register your Reader as an aU component:
```yaml
name: 'default_txt_reader'
description: 'default txt reader'
metadata:
  type: 'READER'
  module: 'agentuniverse.agent.action.knowledge.reader.file.txt_reader'
  class: 'TxtReader'
```
The `metadata.type` must be set to READER.

### Pay Attention to the Package Path of Your Defined Reader:
In the config.toml file of the agentUniverse project, you must configure the package path for the Reader. Ensure that the package path of the file you created is under the `CORE_PACKAGE` in the `reader` path or its subpaths.

For example, in the configuration of the sample project:
```yaml
[CORE_PACKAGE]
reader = ['sample_standard_app.intelligence.agentic.knowledge.reader']
```

## Prebuilt Readers in agentUniverse:
- [default_docx_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/docx_reader.yaml): Reads text content from local Docx files.
- [default_pdf_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/pdf_reader.yaml): Reads text content from local PDF files.
- [default_pptx_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/pptx_reader.yaml): Reads text content from local PPTX files.
- [default_txt_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/txt_reader.yaml): Reads text content from TXT files.
- [default_zip_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/zip_reader.yaml): Reads ZIP archive files, supports nested ZIP structures and multiple file formats.
- [default_web_pdf_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/web_pdf_reader.yaml): Reads text content from PDF files found on the web.
- [default_markdown_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/markdown_reader.yaml): Reads text content from local Markdown files.
- [default_rar_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/rar_reader.yaml): Reads text content from RAR archive files (.rar).
- [default_sevenzip_reader](../../../../../../agentuniverse/agent/action/knowledge/reader/file/sevenzip_reader.yaml): Reads text content from 7Z archive files with preflight safety checks and nested archive support.

### Archive reader safety

`SevenZipReader` validates every archive member before extraction. Members with absolute or drive-qualified paths, backslashes, NUL bytes, `..` path segments, symlinks, or special file types are rejected, as are encrypted archives. File count, per-file size, total uncompressed size, and compression ratio limits are applied from archive metadata before any member is written to disk. Nested archives are charged against the same aggregate budgets before later outer entries are read, and the maximum nesting depth is enforced without reopening deep archives through a reader that would reset those limits. Extracted targets are also checked to ensure they remain inside the temporary directory and match the declared uncompressed size.
