# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: docx_reader.py
import logging
from typing import Union
from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderDependencyError,
)
from agentuniverse.agent.action.knowledge.store.document import Document

logger = logging.getLogger(__name__)


class DocxReader(Reader):
    """Docx reader."""

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the docx file.

        Note:
            The docx file cannot be process in pagination.
            `docx2txt` is required to read DOCX files: `pip install docx2txt`
        """
        try:
            import docx2txt
        except ImportError:
            raise ReaderDependencyError(
                "docx2txt is required to read Microsoft Word files",
                reader_name="DocxReader",
                dependency="docx2txt",
                install_hint="pip install docx2txt",
            )

        if isinstance(file, str):
            file = Path(file)
        if not file.exists():
            raise ReaderLoadError(
                f"DOCX file not found: {file}",
                reader_name="DocxReader",
                source=str(file),
            )

        logger.info("DocxReader start load file=%s", file)
        text = docx2txt.process(file)
        logger.info("DocxReader extracted text length=%d from %s", len(text) if text else 0, file.name)

        metadata = {"file_name": file.name}
        if ext_info is not None:
            metadata.update(ext_info)

        return [Document(text=text, metadata=metadata or {})]
