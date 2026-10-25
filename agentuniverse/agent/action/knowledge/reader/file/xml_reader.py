# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: xml_reader.py

"""
XML file reader with structure-preserving text extraction.

XML is a common interchange shape for structured exports (config dumps,
catalog feeds, telemetry archives, government/enterprise data drops), but
the file readers covered txt/pdf/office/csv/archives only — an ``.xml``
export had no ingestion path, and flattening one with a generic text
reader throws away exactly the structure that makes it useful.

This reader parses with the stdlib ``xml.etree.ElementTree`` — **no new
dependency** — and serializes the tree into retrieval-friendly lines of
``element/path: text`` (document order, mixed-content tails included), so
a recalled chunk carries its structural context instead of a bag of
words. Namespace URIs are stripped to local names for readability;
comments and processing instructions are ignored by the parser.

XML from untrusted sources is hostile input, so parsing is guarded:

* any ``<!DOCTYPE`` or ``<!ENTITY`` declaration is rejected *before*
  parsing; a parser-level guard also rejects DTDs in UTF-16 and other
  supported encodings — this closes both XXE (external entity resolution) and
  entity-expansion bombs ("billion laughs") deterministically, at the
  cost of refusing DTD-bearing documents (a deliberate trade for a
  knowledge-ingestion reader: data exports do not need DTDs);
* ``max_file_bytes`` (default 10 MiB) is enforced via ``stat`` before
  reading a path and via a bounded read for file-like objects;
* ``max_depth`` (default 64) rejects pathologically nested documents
  while parsing, before an oversized tree is built.

Malformed XML and bound violations raise ``ValueError`` (same convention
as the other file readers); wrong configuration types fail loudly at
component-load time.
"""

import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from typing import Any

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

_DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
_DEFAULT_MAX_DEPTH = 64

# Case-insensitive markers scanned on the raw bytes before parsing.
_DTD_MARKERS = (b"<!doctype", b"<!entity")


def _local_name(tag: Any) -> str:
    """Strip the namespace URI from a tag/attribute name."""
    if not isinstance(tag, str):
        return ""
    return tag.split("}", 1)[-1] if tag.startswith("{") else tag


def _collapse(text: str | None) -> str:
    """Normalize whitespace runs; empty when nothing meaningful is left."""
    return " ".join((text or "").split())


class _GuardedTreeBuilder(ET.TreeBuilder):
    """Reject DTDs and excessive depth during parsing, for every encoding."""

    def __init__(self, max_depth: int) -> None:
        super().__init__()
        self.max_depth = max_depth
        self.depth = 0

    def doctype(self, name, pubid, system) -> None:
        raise ValueError("XML contains a DTD/ENTITY declaration; refusing to parse (XXE and entity-expansion guard).")

    def start(self, tag, attrs):
        self.depth += 1
        if self.depth > self.max_depth:
            raise ValueError(f"XML nesting exceeds max_depth={self.max_depth}; refusing to parse.")
        return super().start(tag, attrs)

    def end(self, tag):
        element = super().end(tag)
        self.depth -= 1
        return element


class _WalkState:
    """Mutable counters shared across the recursive walk."""

    def __init__(self) -> None:
        self.element_count = 0


class XmlReader(Reader):
    """XML file reader producing one structure-serialized Document.

    Accepts a path string, ``Path``, or a binary file-like object.

    Attributes:
        max_file_bytes: Maximum accepted file size, enforced before the
            content is fully read.
        max_depth: Maximum accepted element nesting depth.
        include_attributes: When True, each element's attributes are
            emitted as an extra ``path [attributes]: k="v" ...`` line.
    """

    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES
    max_depth: int = _DEFAULT_MAX_DEPTH
    include_attributes: bool = False

    def _load_data(self, file: str | Path | object, ext_info: dict | None = None) -> list[Document]:
        """Parse one XML file into a single Document.

        Args:
            file: Path string, ``Path``, or binary file-like object.
            ext_info: Extra metadata merged onto the produced Document.

        Returns:
            A one-element list with the serialized XML Document. Metadata
            carries ``file_name``, ``root_tag`` and ``element_count``.

        Raises:
            ValueError: If the input is missing, oversized, DTD-bearing,
                too deeply nested, or not well-formed XML.
            TypeError: If ``file`` is neither a path nor a binary file-like
                object.
        """
        self._validate_config()
        raw, file_name = self._read_bytes(file)
        self._reject_dtd(raw, file_name)
        try:
            parser = ET.XMLParser(target=_GuardedTreeBuilder(self.max_depth))
            root = ET.parse(BytesIO(raw), parser=parser).getroot()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML file {file_name}: {e}") from e
        lines: list[str] = []
        state = _WalkState()
        self._walk(root, "", 1, lines, state)
        metadata: dict[str, Any] = {
            "file_name": file_name,
            "root_tag": _local_name(root.tag),
            "element_count": state.element_count,
        }
        if ext_info:
            metadata.update(ext_info)
        return [Document(text="\n".join(lines), metadata=metadata)]

    # ------------------------------------------------------------------ #
    # Serialization
    # ------------------------------------------------------------------ #
    def _walk(self, elem: ET.Element, parent_path: str, depth: int, lines: list[str], state: _WalkState) -> None:
        """Depth-first, document-order serialization of one subtree.

        Raises:
            ValueError: When nesting exceeds ``max_depth`` — checked before
                recursing, so the interpreter's recursion limit is never
                approached by a hostile document.
        """
        if depth > self.max_depth:
            raise ValueError(f"XML nesting exceeds max_depth={self.max_depth}; refusing to parse.")
        if not isinstance(elem.tag, str):
            # Defensive: the default parser drops comments/PIs, but never
            # serialize a non-element node if one ever slips through.
            return
        state.element_count += 1
        local = _local_name(elem.tag)
        path = f"{parent_path}/{local}" if parent_path else local
        text = _collapse(elem.text)
        if text:
            lines.append(f"{path}: {text}")
        if self.include_attributes and elem.attrib:
            rendered = " ".join(f'{_local_name(key)}="{value}"' for key, value in elem.attrib.items())
            lines.append(f"{path} [attributes]: {rendered}")
        for child in elem:
            self._walk(child, path, depth + 1, lines, state)
            # Mixed content: a child's tail text belongs to this element's
            # narrative flow and follows the child's subtree in document order.
            tail = _collapse(child.tail)
            if tail:
                lines.append(f"{path}: {tail}")

    # ------------------------------------------------------------------ #
    # Input handling and guards
    # ------------------------------------------------------------------ #
    def _read_bytes(self, file: str | Path | object) -> tuple[bytes, str]:
        """Read the raw document with the size bound enforced up front.

        Raises:
            ValueError: When the file is missing or exceeds max_file_bytes.
            TypeError: When ``file`` is not a path or binary file-like object.
        """
        if isinstance(file, str):
            file = Path(file)
        if isinstance(file, Path):
            if not file.exists():
                raise ValueError(f"XML file not found: {file}")
            size = file.stat().st_size
            if size > self.max_file_bytes:
                raise ValueError(
                    f"XML file {file.name} is {size} bytes, exceeding max_file_bytes={self.max_file_bytes}."
                )
            return file.read_bytes(), file.name
        if hasattr(file, "read"):
            raw = file.read(self.max_file_bytes + 1)
            if isinstance(raw, str):
                raise TypeError("XML input must be opened in binary mode")
            if not isinstance(raw, bytes | bytearray):
                raise TypeError("Unsupported file object type")
            if len(raw) > self.max_file_bytes:
                raise ValueError(f"XML content exceeds max_file_bytes={self.max_file_bytes}.")
            name_attr = getattr(file, "name", None)
            file_name = Path(name_attr).name if isinstance(name_attr, str) else "unknown"
            return bytes(raw), file_name
        raise TypeError("file must be a path string, Path, or file-like object")

    def _reject_dtd(self, raw: bytes, file_name: str) -> None:
        """Refuse DTD-bearing documents before the parser ever sees them.

        A single deterministic pre-scan closes both XXE and entity-expansion
        bombs; legitimate data exports do not carry DTDs.

        Raises:
            ValueError: When a ``<!DOCTYPE`` or ``<!ENTITY`` declaration is
                present.
        """
        lowered = raw.lower()
        for marker in _DTD_MARKERS:
            if marker in lowered:
                raise ValueError(
                    f"XML file {file_name} contains a DTD/ENTITY declaration; refusing to parse "
                    "(XXE and entity-expansion guard). Remove the DOCTYPE/ENTITY for ingestion."
                )

    # ------------------------------------------------------------------ #
    # Configuration validation
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Fail loudly on configuration that would weaken a safety bound.

        Raises:
            TypeError: On wrong field types.
            ValueError: On non-positive bounds.
        """
        if not isinstance(self.max_file_bytes, int) or isinstance(self.max_file_bytes, bool):
            raise TypeError(f"max_file_bytes must be an integer, got {self.max_file_bytes!r}.")
        if self.max_file_bytes < 1:
            raise ValueError(f"max_file_bytes must be a positive integer, got {self.max_file_bytes!r}.")
        if not isinstance(self.max_depth, int) or isinstance(self.max_depth, bool):
            raise TypeError(f"max_depth must be an integer, got {self.max_depth!r}.")
        if self.max_depth < 1:
            raise ValueError(f"max_depth must be a positive integer, got {self.max_depth!r}.")
        if not isinstance(self.include_attributes, bool):
            raise TypeError(f"include_attributes must be a boolean, got {self.include_attributes!r}.")

    def _initialize_by_component_configer(self, reader_configer: ComponentConfiger) -> "XmlReader":
        """Initialize the reader from its component config."""
        super()._initialize_by_component_configer(reader_configer)
        for attr in ("max_file_bytes", "max_depth", "include_attributes"):
            if hasattr(reader_configer, attr):
                setattr(self, attr, getattr(reader_configer, attr))
        # Validate eagerly so a misconfigured bound fails at component-load
        # time rather than silently at read time.
        self._validate_config()
        return self
