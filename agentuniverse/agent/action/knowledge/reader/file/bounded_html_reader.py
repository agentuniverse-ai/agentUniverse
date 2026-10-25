# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: bounded_html_reader.py

"""Bounded HTML (.html/.htm) reader.

Renders markup to retrieval text with the stdlib :mod:`html.parser` only (no
BeautifulSoup): ``script``/``style``/``noscript``/``template`` content and
comments are dropped, block-level tags become line breaks, the ``<title>`` goes
to metadata (``html_title``) instead of polluting the body, runs of blank lines
collapse, and the result is truncated to ``max_text_chars``. Encoding: BOM
detection plus a ``<meta charset>`` sniff, then UTF-8 with replacement. Reads at
most ``max_file_bytes`` plus one probe byte, so an oversized page fails loudly
with a ValueError quoting the offending size instead of ballooning memory.

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003
"""

import codecs
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

_DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
_DEFAULT_MAX_TEXT_CHARS = 200_000
_MAX_HEADER_CHARS = 2000
_SKIP_TAGS = frozenset({"script", "style", "noscript", "template"})
_BREAK_TAGS = frozenset({
    "address", "article", "aside", "br", "dd", "div", "dl", "dt", "fieldset",
    "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5",
    "h6", "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section",
    "table", "tbody", "td", "tfoot", "th", "thead", "tr", "ul",
})
_META_CHARSET_RE = re.compile(rb"charset\s*=\s*[\"']?([A-Za-z0-9_\-]+)")


class _HtmlTextExtractor(HTMLParser):
    """Buffer text, drop skips/comments, mark block ends as newlines."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: List[str] = []
        self._skip_depth = 0
        self._in_title = 0
        self.title = ""

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title" and self._in_title:
            self._in_title -= 1
        if tag in _BREAK_TAGS:
            self._chunks.append("\n")

    def handle_startendtag(self, tag: str, attrs) -> None:
        if tag.lower() in _BREAK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not data or self._skip_depth:
            return
        if self._in_title:
            if self._in_title == 1:
                self.title += data
            return
        collapsed = " ".join(data.split())
        if collapsed:
            self._chunks.append(collapsed)

    def text(self) -> str:
        lines: List[str] = []
        for chunk in "".join(self._chunks).split("\n"):
            line = " ".join(chunk.split())
            if line or (lines and lines[-1]):
                lines.append(line)
        return "\n".join(lines).strip()


def html_to_text(markup: str) -> str:
    """Render an HTML string to bounded retrieval text (shared with the EML reader)."""
    extractor = _HtmlTextExtractor()
    extractor.feed(markup)
    extractor.close()
    return extractor.text()


def _decode_html(data: bytes) -> str:
    for bom, encoding in (
            (codecs.BOM_UTF8, "utf-8-sig"),
            (codecs.BOM_UTF32_LE, "utf-32"),
            (codecs.BOM_UTF32_BE, "utf-32"),
            (codecs.BOM_UTF16_LE, "utf-16"),
            (codecs.BOM_UTF16_BE, "utf-16"),
    ):
        if data.startswith(bom):
            return data.decode(encoding, errors="replace")
    head = data[:2048]
    match = _META_CHARSET_RE.search(head)
    if match:
        try:
            return data.decode(match.group(1).decode("ascii"), errors="replace")
        except LookupError:
            pass
    return data.decode("utf-8", errors="replace")


def _collapse(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.split())[:_MAX_HEADER_CHARS]


class BoundedHtmlReader(Reader):
    """Bounded, stdlib-only HTML reader (supersedes #3329's HtmlFileReader)."""

    max_file_bytes: int = _DEFAULT_MAX_FILE_BYTES
    max_text_chars: int = _DEFAULT_MAX_TEXT_CHARS

    def _load_data(self, file: Path, ext_info: Optional[Dict] = None) -> List[Document]:
        self._validate_config()
        with file.open("rb") as handle:
            data = handle.read(self.max_file_bytes + 1)
        if len(data) > self.max_file_bytes:
            raise ValueError(
                f"HTML file is {len(data)!r} bytes, exceeding max_file_bytes="
                f"{self.max_file_bytes!r}: {file!s}")
        extractor = _HtmlTextExtractor()
        extractor.feed(_decode_html(data))
        extractor.close()
        metadata: Dict = {"file_name": file.name}
        title = _collapse(extractor.title)
        if title:
            metadata["html_title"] = title
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=extractor.text()[:self.max_text_chars], metadata=metadata)]

    def _validate_config(self) -> None:
        for attr in ("max_file_bytes", "max_text_chars"):
            bound = getattr(self, attr)
            if not isinstance(bound, int) or isinstance(bound, bool) or bound <= 0:
                raise ValueError(f"{attr} must be a positive int, got {bound!r}")

    def _initialize_by_component_configer(
            self, reader_configer: ComponentConfiger) -> "BoundedHtmlReader":
        super()._initialize_by_component_configer(reader_configer)
        for attr in ("max_file_bytes", "max_text_chars"):
            if hasattr(reader_configer, attr):
                setattr(self, attr, getattr(reader_configer, attr))
        self._validate_config()
        return self
