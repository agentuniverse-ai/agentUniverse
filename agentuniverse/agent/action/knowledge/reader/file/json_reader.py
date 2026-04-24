# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import Union
from pathlib import Path
from typing import List, Optional, Dict
import json

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding


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
            ImportError: Never raised (json is a standard library)
            json.JSONDecodeError: If the file contains invalid JSON
            FileNotFoundError: If the file does not exist
        """
        if isinstance(file, str):
            file = Path(file)

        if not file.exists():
            raise FileNotFoundError(f"JSON file not found: {file}")

        # Detect file encoding for proper reading
        encoding = detect_file_encoding(file)

        # Read and parse JSON file
        with open(file, 'r', encoding=encoding) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Invalid JSON in file {file.name}: {str(e)}",
                    e.doc,
                    e.pos
                )

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

        return [Document(text=text, metadata=metadata or {})]
