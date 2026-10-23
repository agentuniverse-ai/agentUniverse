# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Read JSON Lines corpora as individual knowledge documents."""
import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


def _reject_constant(value: str) -> None:
    """Reject non-JSON numeric constants accepted by Python's decoder."""
    raise ValueError(f"Invalid JSON constant: {value}")


class JsonlReader(Reader):
    """UTF-8 JSONL/NDJSON reader with one Document per nonblank line."""

    def _load_data(self, file: Union[str, Path],
                   ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse a JSON Lines file without loading the entire source at once.

        Args:
            file: Path to a UTF-8 file, without a byte order mark.
            ext_info: Additional metadata, overriding generated metadata keys.

        Returns:
            Documents containing original JSON records and physical line numbers.
            Blank lines are ignored; an empty file returns an empty list.

        Raises:
            ValueError: A record is invalid JSON. Includes its file and line.
            UnicodeDecodeError: The file is not UTF-8.
            OSError: The file cannot be opened or read.
        """
        file = Path(file)
        documents = []
        with file.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line, parse_constant=_reject_constant)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid JSON in {file} at line {line_number}: {exc}"
                    ) from exc

                if isinstance(data, dict):
                    json_type = "object"
                elif isinstance(data, list):
                    json_type = "array"
                else:
                    json_type = "primitive"
                metadata = {
                    "file_name": file.name,
                    "file_path": str(file),
                    "line_number": line_number,
                    "json_type": json_type,
                }
                if ext_info is not None:
                    metadata.update(ext_info)
                documents.append(Document(
                    text=line.strip(),
                    metadata=metadata,
                ))
        return documents
