# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Reader for XML knowledge files."""

from pathlib import Path
from typing import Dict, List, Optional, Union
from xml.etree import ElementTree

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding
from agentuniverse.agent.action.knowledge.store.document import Document


class XmlReader(Reader):
    """Validate an XML file and load it as one source-preserving Document."""

    def _load_data(self, file: Union[str, Path],
                   ext_info: Optional[Dict] = None) -> List[Document]:
        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path):
            raise TypeError(f"XML file must be a path, got {type(file).__name__}")
        if not file.exists():
            raise FileNotFoundError(f"XML file not found: {file}")
        if not file.is_file():
            raise IsADirectoryError(f"XML path is not a file: {file}")

        raw = file.read_bytes()
        try:
            root = ElementTree.fromstring(raw)
        except (ElementTree.ParseError, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid XML in {file.name}: {exc}") from exc

        root_tag = root.tag.rsplit("}", 1)[-1] if "}" in root.tag else root.tag
        metadata = {
            "file_name": file.name,
            "file_path": str(file),
            "root_tag": root_tag,
            "format": "xml",
        }
        if ext_info is not None:
            metadata.update(ext_info)
        encoding = detect_file_encoding(raw)
        metadata["encoding"] = encoding
        return [Document(text=raw.decode(encoding), metadata=metadata)]
