# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/2 22:00
# @Author  : wangyapei
# @FileName: csv_reader.py

import csv
import io
from pathlib import Path
from typing import List, Union, Optional, Dict, TextIO

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding


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
                    raise FileNotFoundError(f"File not found: {file}")
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
                    raise ValueError("Unsupported file object type")
                should_close = True
            else:
                raise TypeError("file must be a path string, Path, or file-like object")

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

            return [Document(text=final_content, metadata=metadata)]
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}") from e
