# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/2 22:00
# @Author  : wangyapei
# @FileName: csv_reader.py

import csv
import io
import logging
from pathlib import Path
from typing import List, Union, Optional, Dict, TextIO

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderConfigError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding

logger = logging.getLogger(__name__)


class CSVReader(Reader):
    """CSV file reader.

    Used to read and parse CSV format files, supports local file paths or file objects as input.
    """

    def _load_data(self,
                  file: Union[str, Path, TextIO],
                  delimiter: str = ",",
                  quotechar: str = '"',
                  ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse CSV file."""
        try:
            text_stream: TextIO
            should_close = False

            if isinstance(file, str):
                file = Path(file)

            if isinstance(file, Path):
                if not file.exists():
                    raise ReaderLoadError(
                        f"CSV file not found: {file}",
                        reader_name="CSVReader",
                        source=str(file),
                    )
                encoding = detect_file_encoding(file)
                text_stream = file.open(newline="", mode="r", encoding=encoding)
                should_close = True
            elif hasattr(file, "read"):
                try:
                    file.seek(0)
                except (AttributeError, OSError):
                    pass
                raw_content = file.read()
                if isinstance(raw_content, bytes):
                    encoding = detect_file_encoding(raw_content)
                    text_stream = io.StringIO(raw_content.decode(encoding))
                elif isinstance(raw_content, str):
                    text_stream = io.StringIO(raw_content)
                else:
                    raise ReaderConfigError(
                        "Unsupported file object type",
                        reader_name="CSVReader",
                    )
                should_close = True
            else:
                raise ReaderConfigError(
                    "file must be a path string, Path, or file-like object",
                    reader_name="CSVReader",
                )

            csv_content: List[str] = []
            try:
                csv_reader = csv.reader(text_stream, delimiter=delimiter, quotechar=quotechar)
                for row in csv_reader:
                    if any(cell.strip() for cell in row):
                        while row and not row[-1].strip():
                            row.pop()
                        csv_content.append(", ".join(filter(None, row)))
            finally:
                if should_close:
                    text_stream.close()

            final_content = "\n".join(csv_content)

            if isinstance(file, Path):
                file_name = file.name
            else:
                name_attr = getattr(file, 'name', None)
                file_name = Path(name_attr).name if isinstance(name_attr, str) else 'unknown'
            metadata = {"file_name": file_name}
            if ext_info:
                metadata.update(ext_info)

            logger.info("CSVReader extracted %d rows from %s", len(csv_content), file_name)
            return [Document(text=final_content, metadata=metadata)]
        except (ReaderLoadError, ReaderConfigError):
            raise
        except Exception as e:
            raise ReaderParseError(
                f"Failed to read CSV file: {e}",
                reader_name="CSVReader",
            ) from e
