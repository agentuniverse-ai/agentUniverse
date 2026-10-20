# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Reader for TOML knowledge files."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.utils import detect_file_encoding
from agentuniverse.agent.action.knowledge.store.document import Document


class TomlReader(Reader):
    """Load a TOML document as formatted structured text."""

    def _load_data(self, file: Union[str, Path],
                   ext_info: Optional[Dict] = None) -> List[Document]:
        try:
            import tomllib
        except ImportError:  # Python 3.10 compatibility
            try:
                import tomli as tomllib
            except ImportError as exc:  # pragma: no cover - optional fallback
                raise ImportError(
                    "tomllib or tomli is required to read TOML files"
                ) from exc

        if isinstance(file, str):
            file = Path(file)
        if not isinstance(file, Path):
            raise TypeError(f"TOML file must be a path, got {type(file).__name__}")
        if not file.exists():
            raise FileNotFoundError(f"TOML file not found: {file}")
        if not file.is_file():
            raise IsADirectoryError(f"TOML path is not a file: {file}")

        encoding = detect_file_encoding(file)
        try:
            with file.open("rb") as stream:
                value = tomllib.load(stream)
        except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"Invalid TOML in {file.name}: {exc}") from exc

        metadata = {
            "file_name": file.name,
            "file_path": str(file),
            "format": "toml",
            "encoding": encoding,
        }
        if ext_info is not None:
            metadata.update(ext_info)
        return [Document(
            text=json.dumps(value, ensure_ascii=False, indent=2, default=str),
            metadata=metadata,
        )]
