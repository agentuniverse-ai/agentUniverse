# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Reader for newline-delimited JSON (JSONL/NDJSON) files."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding
from agentuniverse.agent.action.knowledge.store.document import Document


class JsonlReader(Reader):
    """Load one JSON value per non-empty line as an individual document."""

    def _load_data(self, file: Union[str, Path],
                   ext_info: Optional[Dict] = None) -> List[Document]:
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path):
            raise TypeError(f"JSONL file must be a path, got {type(file).__name__}")
        if not file.exists():
            raise FileNotFoundError(f"JSONL file not found: {file}")
        if not file.is_file():
            raise IsADirectoryError(f"JSONL path is not a file: {file}")

        encoding = detect_file_encoding(file)
        documents: List[Document] = []
        with file.open("r", encoding=encoding) as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    message = (
                        f"Invalid JSONL record in {file.name} at line "
                        f"{line_number}: {exc.msg}"
                    )
                    raise json.JSONDecodeError(message, exc.doc, exc.pos) from exc

                if isinstance(value, dict):
                    json_type = "object"
                elif isinstance(value, list):
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
                    text=json.dumps(value, indent=2, ensure_ascii=False),
                    metadata=metadata,
                ))

        return documents
