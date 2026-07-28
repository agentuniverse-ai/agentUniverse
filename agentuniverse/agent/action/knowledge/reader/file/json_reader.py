# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import logging
from typing import Union
from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderLoadError,
    ReaderParseError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding

logger = logging.getLogger(__name__)


class JsonReader(Reader):
    """JSON file reader."""

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the JSON file.

        Args:
            file: Path to the JSON file (str or Path object)
            ext_info: Optional additional metadata to include in the document

        Returns:
            List[Document]: A list containing a single Document with the JSON content
                           formatted as a readable string

        Raises:
            ReaderLoadError: If the file does not exist
            ReaderParseError: If the file contains invalid JSON
        """
        if isinstance(file, str):
            file = Path(file)

        if not file.exists():
            raise ReaderLoadError(
                f"JSON file not found: {file}",
                reader_name="JsonReader",
                source=str(file),
            )

        logger.info("JsonReader start load file=%s", file)

        # Detect file encoding for proper reading
        encoding = detect_file_encoding(file)

        # Read and parse JSON file
        with open(file, 'r', encoding=encoding) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ReaderParseError(
                    f"Invalid JSON in file {file.name}: {e}",
                    reader_name="JsonReader",
                    source=str(file),
                ) from e

        # Convert JSON data to formatted string
        text = json.dumps(data, indent=2, ensure_ascii=False)

        # Determine JSON type for metadata
        if isinstance(data, dict):
            json_type = "object"
        elif isinstance(data, list):
            json_type = "array"
        else:
            json_type = "primitive"

        # Build metadata
        metadata = {
            "file_name": file.name,
            "file_path": str(file),
            "json_type": json_type
        }
        if ext_info is not None:
            metadata.update(ext_info)

        logger.info("JsonReader extracted text length=%d from %s", len(text), file.name)
        return [Document(text=text, metadata=metadata or {})]
