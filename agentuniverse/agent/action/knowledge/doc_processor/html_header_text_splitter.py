# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/20
# @FileName: html_header_text_splitter.py

"""
HTML header text splitter — a knowledge pre-processing DocProcessor.

Splits each input ``Document`` into one chunk per HTML header section
(<h1>–<h6>), recording the header hierarchy as metadata so a retrieved
chunk can be traced back to where it came from. This is the HTML analogue
of the merged ``MarkdownHeaderTextSplitter`` (#625) and fills the *HTML
pre-processing* direction of #258.

It is intentionally dependency-light: it uses Python's built-in
``html.parser.HTMLParser`` so it works without ``beautifulsoup4`` / ``lxml``
installed, and is fully unit-testable without a network connection.
"""

import logging
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

_HEADER_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
# Tags whose content should not appear in the output text.
_SKIP_TAGS = {"script", "style", "noscript", "head", "meta", "link", "title"}
# Block-level tags that imply a line break when converting to plain text.
_BLOCK_TAGS = {"p", "div", "br", "li", "tr", "table", "ul", "ol", "blockquote"}


class _HtmlHeaderSplitParser(HTMLParser):
    """Parse HTML and emit (header_path, text) chunks.

    Tracks the current h1–h6 hierarchy. When a new header at any level is
    encountered, the text accumulated so far is flushed as a chunk for the
    previous header path, and a new chunk begins under the new path.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._headers: Dict[int, str] = {}  # level -> title
        self._chunks: List[Tuple[str, str]] = []
        self._current_text: List[str] = []
        self._skip_depth = 0
        self._in_header_level: Optional[int] = None
        self._header_text_buf: List[str] = []

    # -- public --
    def get_chunks(self) -> List[Tuple[str, str]]:
        """Return (header_path, text) pairs."""
        self._flush()
        return [(p, t) for p, t in self._chunks if t and t.strip()]

    # -- internal --
    def _header_path(self) -> str:
        parts = [self._headers[lv] for lv in sorted(self._headers) if lv in self._headers]
        return " > ".join(parts)

    def _push_header(self, level: int, title: str) -> None:
        self._headers[level] = title.strip()
        for lv in list(self._headers):
            if lv > level:
                del self._headers[lv]

    def _flush(self) -> None:
        text = "".join(self._current_text).strip()
        if text:
            self._chunks.append((self._header_path(), text))
        self._current_text = []

    def _append_text(self, data: str) -> None:
        if self._in_header_level is not None:
            self._header_text_buf.append(data)
        else:
            self._current_text.append(data)

    # -- HTMLParser overrides --
    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in _HEADER_TAGS:
            # Flush previous chunk before starting a new header section.
            self._flush()
            self._in_header_level = int(tag[1])
            self._header_text_buf = []
        elif tag in _BLOCK_TAGS and self._current_text:
            self._current_text.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _SKIP_TAGS:
            if self._skip_depth > 0:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in _HEADER_TAGS:
            title = "".join(self._header_text_buf).strip()
            if title:
                self._push_header(self._in_header_level, title)
            self._in_header_level = None
            self._header_text_buf = []
        elif tag in _BLOCK_TAGS:
            self._current_text.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self._append_text(data)


class HtmlHeaderTextSplitter(DocProcessor):
    """Pre-processing splitter that chunks HTML by header hierarchy.

    Attributes:
        header_path_key: Metadata key under which each chunk's header path
            (e.g. ``"Installation > macOS"``) is recorded.
        include_unsectioned: If ``True`` (default), text before the first
            header is emitted as a chunk with an empty header path. If
            ``False``, it is dropped.
    """

    header_path_key: str = "header_path"
    include_unsectioned: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query=None) -> List[Document]:
        """Split each document's text by HTML headers."""
        if not origin_docs:
            return []
        result: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            for header_path, chunk_text in self._split_html(text):
                if not header_path and not self.include_unsectioned:
                    continue
                meta = dict(doc.metadata or {})
                meta[self.header_path_key] = header_path
                result.append(Document(text=chunk_text, metadata=meta))
        return result

    @staticmethod
    def _split_html(html: str) -> List[Tuple[str, str]]:
        """Parse ``html`` and return (header_path, text) pairs."""
        parser = _HtmlHeaderSplitParser()
        parser.feed(html)
        parser.close()
        return parser.get_chunks()

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> "HtmlHeaderTextSplitter":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "header_path_key"):
            self.header_path_key = doc_processor_configer.header_path_key
        if hasattr(doc_processor_configer, "include_unsectioned"):
            self.include_unsectioned = doc_processor_configer.include_unsectioned
        return self
