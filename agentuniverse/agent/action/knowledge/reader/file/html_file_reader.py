# !/usr/bin/env python3

# @Time    : 2026/10/03
# @FileName: html_file_reader.py

"""
Local HTML file reader.

Saved pages, report exports, crawled snapshots and documentation drops
routinely land on disk as ``.html`` / ``.htm`` files. The existing
``website_bs4_reader`` fetches a **URL** over the network; there was no
reader for HTML that already exists as a local file — ingesting an export
directory meant either serving it over HTTP or hand-converting it. This
reader fills that gap using the BeautifulSoup dependency the framework
already ships: **no new dependency, and no network access at all** (the
file is parsed strictly as data; remote resources referenced by the
markup are never fetched).

Each file produces one Document:

* text — an optional ``Title: ...`` line followed by the visible text
  (one stripped line per text node), truncated to ``max_text_chars``;
* metadata — ``file_name``, ``html_title`` / ``html_description`` (from
  ``<title>`` and the description ``<meta>`` when present),
  ``text_length`` after truncation, plus caller ``ext_info``.

Non-content markup is removed before extraction: ``<script>``,
``<style>``, ``<noscript>``, ``<template>`` subtrees and HTML comments —
so JavaScript source, CSS rules and boilerplate comments never leak into
knowledge chunks.

Safety bounds (exported pages are untrusted input):

* ``max_file_bytes`` (default 10 MiB) is enforced via ``stat`` before
  reading a path, and via a bounded read for file-like objects;
* ``max_text_chars`` (default 200,000) caps the extracted text so one
  pathological page cannot flood downstream chunking/embedding;
* bound misconfiguration fails loudly at component-load time; missing or
  unreadable input raises ``ValueError`` (same convention as the other
  file readers), and text-mode streams or invalid input types raise a
  clear ``TypeError``.
"""

import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Comment

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

logger = logging.getLogger(__name__)

_DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
_DEFAULT_MAX_TEXT_CHARS = 200_000

# Non-content subtrees removed before text extraction.
_STRIPPED_TAGS = ("script", "style", "noscript", "template")

_BLANK_RUN_RE = re.compile(r"\n{2,}")


class HtmlFileReader(Reader):
    """Reader for local HTML files (.html / .htm).

    Accepts a path string, ``Path``, or a binary file-like object, and
    returns exactly one Document per file.

    Attributes:
        max_file_bytes: Maximum accepted file size, enforced before the
            content is fully read.
        max_text_chars: Hard truncation bound on the extracted text.
        include_title_in_text: When True (default) and a ``<title>``
            exists, a ``Title: ...`` line is prepended to the text so
            retrieval can match on it; metadata carries the title either
            way.
    """

    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES
    max_text_chars: int = _DEFAULT_MAX_TEXT_CHARS
    include_title_in_text: bool = True

    def _load_data(self, file: str | Path | object, ext_info: dict | None = None) -> list[Document]:
        """Parse one local HTML file into a single Document.

        Args:
            file: Path string, ``Path``, or binary file-like object.
            ext_info: Extra metadata merged onto the produced Document.

        Returns:
            A one-element list with the extracted Document.

        Raises:
            ValueError: If the input is missing, oversized, or unreadable.
            TypeError: If ``file`` is not a path or a binary file-like object.
        """
        self._validate_config()
        raw, file_name = self._read_bytes(file)
        # BeautifulSoup detects the declared/actual encoding from the raw
        # bytes; the document is parsed strictly as data — no remote
        # resource referenced by the markup is ever fetched.
        soup = BeautifulSoup(BytesIO(raw), "html.parser")
        self._strip_non_content(soup)
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        text = self._extract_text(soup, title)
        metadata: dict[str, Any] = {
            "file_name": file_name,
            "text_length": len(text),
        }
        if title:
            metadata["html_title"] = title
        if description:
            metadata["html_description"] = description
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #
    def _strip_non_content(self, soup: BeautifulSoup) -> None:
        """Remove script/style/noscript/template subtrees and comments."""
        for tag_name in _STRIPPED_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        for comment in soup.find_all(string=lambda item: isinstance(item, Comment)):
            comment.extract()

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str | None:
        """Return the collapsed <title> text, or None when absent/empty."""
        if soup.title is None:
            return None
        title = " ".join(soup.title.get_text().split())
        return title or None

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> str | None:
        """Return the description <meta> content when present."""
        tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        if tag is None:
            return None
        content = tag.get("content")
        if not isinstance(content, str):
            return None
        content = " ".join(content.split())
        return content or None

    def _extract_text(self, soup: BeautifulSoup, title: str | None) -> str:
        """Visible text, one stripped line per node, capped and optionally
        title-prefixed."""
        body_text = soup.get_text("\n", strip=True)
        body_text = _BLANK_RUN_RE.sub("\n", body_text).strip()
        if self.include_title_in_text and title:
            body_text = f"Title: {title}\n{body_text}".strip()
        return body_text[: self.max_text_chars]

    # ------------------------------------------------------------------ #
    # Input handling
    # ------------------------------------------------------------------ #
    def _read_bytes(self, file: str | Path | object) -> tuple[bytes, str]:
        """Read the raw file with the size bound enforced up front.

        Raises:
            ValueError: When the file is missing or exceeds max_file_bytes.
            TypeError: When ``file`` is not a path or binary file-like object.
        """
        if isinstance(file, str):
            file = Path(file)
        if isinstance(file, Path):
            if not file.exists():
                raise ValueError(f"HTML file not found: {file}")
            size = file.stat().st_size
            if size > self.max_file_bytes:
                raise ValueError(
                    f"HTML file {file.name} is {size} bytes, exceeding max_file_bytes={self.max_file_bytes}."
                )
            return file.read_bytes(), file.name
        if hasattr(file, "read"):
            raw = file.read(self.max_file_bytes + 1)
            if isinstance(raw, str):
                raise TypeError("HTML input must be opened in binary mode")
            if not isinstance(raw, bytes | bytearray):
                raise TypeError("Unsupported file object type")
            if len(raw) > self.max_file_bytes:
                raise ValueError(f"HTML content exceeds max_file_bytes={self.max_file_bytes}.")
            name_attr = getattr(file, "name", None)
            file_name = Path(name_attr).name if isinstance(name_attr, str) else "unknown"
            return bytes(raw), file_name
        raise TypeError("file must be a path string, Path, or file-like object")

    # ------------------------------------------------------------------ #
    # Configuration validation
    # ------------------------------------------------------------------ #
    def _validate_config(self) -> None:
        """Fail loudly on configuration that would weaken a safety bound.

        Raises:
            TypeError: On wrong field types.
            ValueError: On non-positive bounds.
        """
        for attr in ("max_file_bytes", "max_text_chars"):
            value = getattr(self, attr)
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{attr} must be an integer, got {value!r}.")
            if value < 1:
                raise ValueError(f"{attr} must be a positive integer, got {value!r}.")
        if not isinstance(self.include_title_in_text, bool):
            raise TypeError(f"include_title_in_text must be a boolean, got {self.include_title_in_text!r}.")

    def _initialize_by_component_configer(self, reader_configer: ComponentConfiger) -> "HtmlFileReader":
        """Initialize the reader from its component config."""
        super()._initialize_by_component_configer(reader_configer)
        for attr in ("max_file_bytes", "max_text_chars", "include_title_in_text"):
            if hasattr(reader_configer, attr):
                setattr(self, attr, getattr(reader_configer, attr))
        # Validate eagerly so a misconfigured bound fails at component-load
        # time rather than silently at read time.
        self._validate_config()
        return self
