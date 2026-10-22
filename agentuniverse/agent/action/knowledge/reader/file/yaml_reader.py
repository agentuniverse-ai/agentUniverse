# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Reader for YAML and YML knowledge files."""

from pathlib import Path
from typing import Dict, List, Optional, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding
from agentuniverse.agent.action.knowledge.store.document import Document


class YamlReader(Reader):
    """Load each non-empty YAML document as an independent Document."""

    def _load_data(self, file: Union[str, Path],
                   ext_info: Optional[Dict] = None) -> List[Document]:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - dependency is optional
            raise ImportError(
                "PyYAML is required to read YAML files: pip install pyyaml"
            ) from exc

        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path):
            raise TypeError(f"YAML file must be a path, got {type(file).__name__}")
        if not file.exists():
            raise FileNotFoundError(f"YAML file not found: {file}")
        if not file.is_file():
            raise IsADirectoryError(f"YAML path is not a file: {file}")

        encoding = detect_file_encoding(file)
        with file.open("r", encoding=encoding) as stream:
            try:
                values = list(yaml.safe_load_all(stream))
            except yaml.YAMLError as exc:
                raise ValueError(f"Invalid YAML in {file.name}: {exc}") from exc

        documents: List[Document] = []
        for document_index, value in enumerate(values, start=1):
            if value is None:
                continue
            metadata = {
                "file_name": file.name,
                "file_path": str(file),
                "document_index": document_index,
            }
            if ext_info is not None:
                metadata.update(ext_info)
            documents.append(Document(
                text=yaml.safe_dump(value, allow_unicode=True, sort_keys=False),
                metadata=metadata,
            ))
        return documents
