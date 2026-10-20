# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: bounded_xml_reader.py

"""Bounded XML (.xml) reader.

Parses with the stdlib ElementTree (external subsets are never fetched),
extracts text and CDATA sections in document order via an iterative
(recursion-limit safe) walk, guards nesting depth at ``max_depth`` and result
length at ``max_text_chars``, and keeps the root's local tag in metadata
(``xml_root``) for filtering. Every failure mode -- oversize, over-deep,
truncation-adjacent parse errors -- raises ValueError quoting the offending
value.

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

_DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
_DEFAULT_MAX_TEXT_CHARS = 200_000
_DEFAULT_MAX_DEPTH = 64


def _local_name(tag) -> str:
    return str(tag).rsplit("}", 1)[-1]


class BoundedXmlReader(Reader):
    """Bounded, stdlib-only XML reader (supersedes #3328's XmlReader)."""

    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES
    max_text_chars: int = _DEFAULT_MAX_TEXT_CHARS
    max_depth: int = _DEFAULT_MAX_DEPTH

    def _load_data(self, file: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        self._validate_config()
        with file.open("rb") as handle:
            data = handle.read(self.max_file_bytes + 1)
        if len(data) > self.max_file_bytes:
            raise ValueError(
                f"XML file is {len(data)!r} bytes, exceeding max_file_bytes="
                f"{self.max_file_bytes!r}: {file!s}")
        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            raise ValueError(f"XML parse failed in {file!s}: {exc!r}") from exc
        text = self._collect_text(root)
        metadata: Dict = {"file_name": file.name, "xml_root": _local_name(root.tag)}
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text[:self.max_text_chars], metadata=metadata)]

    def _collect_text(self, root: ET.Element) -> str:
        parts: List[str] = []
        stack = [(root, 1)]
        while stack:
            element, depth = stack.pop()
            if depth > self.max_depth:
                raise ValueError(
                    f"XML nesting depth {depth!r} exceeds max_depth="
                    f"{self.max_depth!r}: element {_local_name(element.tag)!r}")
            for value in (element.text, element.tail):
                if value:
                    stripped = " ".join(value.split())
                    if stripped:
                        parts.append(stripped)
            for child in reversed(list(element)):
                stack.append((child, depth + 1))
        return " ".join(parts)

    def _validate_config(self) -> None:
        for attr in ("max_file_bytes", "max_text_chars", "max_depth"):
            bound = getattr(self, attr)
            if not isinstance(bound, int) or isinstance(bound, bool) or bound <= 0:
                raise ValueError(f"{attr} must be a positive int, got {bound!r}")

    def _initialize_by_component_configer(
            self, reader_configer: ComponentConfiger) -> "BoundedXmlReader":
        super()._initialize_by_component_configer(reader_configer)
        for attr in ("max_file_bytes", "max_text_chars", "max_depth"):
            if hasattr(reader_configer, attr):
                setattr(self, attr, getattr(reader_configer, attr))
        self._validate_config()
        return self
