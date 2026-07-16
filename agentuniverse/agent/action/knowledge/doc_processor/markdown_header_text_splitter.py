# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/13
# @FileName: markdown_header_text_splitter.py

"""
Markdown header text splitter.

Splits each input :class:`Document` into one section per markdown header (ATX
headings ``#`` … ``######``), recording the section's header hierarchy as
metadata so a retrieved chunk can be traced back to the part of the document
it came from. This is the *pre-processing* direction of issue #258 (knowledge
pre-processing components): a long markdown source — read from a ``.md`` file,
a crawled web page, a README — is broken into header-delimited chunks *before*
it is embedded and stored.

The component is pure-Python, deterministic, and dependency-free: unlike the
framework's other splitters it does not wrap a third-party library, so it is
fully unit-testable without a network connection or optional install.

It only separates on headers; a section that is still larger than desired
should be chained with a character / token splitter afterwards (splitter
processors compose — the output list is a valid input to the next one).

Fenced code blocks (backtick or tilde fences) are respected: a '#'-prefixed
line inside one is treated as code rather than a header, so code samples in a
README are not mistaken for section titles.
"""

import re
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

# ATX header: 1-6 leading '#', mandatory whitespace, then the title text. A
# trailing run of '#' (closed ATX syntax) and surrounding whitespace are
# stripped. A line such as "#no-space" or "####### seven" is not a header.
_HEADER_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")

# Fenced code blocks (CommonMark). An opening fence is up to three leading
# spaces followed by three or more backticks or tildes; a backtick fence may
# not carry a backtick in its info string. A closing fence is up to three
# leading spaces, the same fence character repeated at least as many times as
# the opening fence, then only trailing whitespace. While inside a fence, ATX
# header detection is suppressed so a '# Example' line inside a ```python
# block is treated as code instead of a header.
_FENCE_OPEN_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})[ \t]*$")


class MarkdownHeaderTextSplitter(DocProcessor):
    """Split markdown documents by their ATX header structure.

    Attributes:
        max_header_level (int): Deepest ATX header level to split on (1–6).
            Headers deeper than this are treated as ordinary content lines,
            so ``max_header_level=1`` splits only on top-level (``#``) headers.
        header_path_key (Optional[str]): Metadata key under which the splitter
            records the joined header hierarchy of each section (e.g.
            ``"Installation > macOS"``). Set to ``None`` to omit the field.
        keep_preamble (bool): When True, content before the first header is
            emitted as its own section (with an empty header path); when False
            it is dropped.
        path_separator (str): Joiner used to compose the header path.
    """

    max_header_level: int = 6
    header_path_key: Optional[str] = "header_path"
    keep_preamble: bool = True
    path_separator: str = " > "

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Split each document into header-delimited sections.

        Args:
            origin_docs (List[Document]): Documents whose ``text`` is parsed as
                markdown. Each document's existing metadata is preserved on the
                emitted sections.
            query (Query, optional): Unused; kept for interface compatibility.

        Returns:
            List[Document]: One document per non-empty section, each carrying
            its header hierarchy under ``header_path_key`` (when configured).
            An empty input yields an empty list.
        """
        if not origin_docs:
            return []
        sections: List[Document] = []
        for doc in origin_docs:
            base_meta = dict(doc.metadata or {})
            for text, header_path in self._split_text(doc.text or ""):
                metadata = dict(base_meta)
                if self.header_path_key:
                    metadata[self.header_path_key] = header_path
                sections.append(Document(text=text, metadata=metadata))
        return sections

    # ------------------------------------------------------------------ #
    # Splitting (pure) — fully testable without a network
    # ------------------------------------------------------------------ #

    def _split_text(self, text: str) -> List[Tuple[str, str]]:
        """Return ``(section_text, header_path)`` pairs for one document."""
        headers: Dict[int, str] = {}  # current open header title per level
        buffer: List[str] = []
        sections: List[Tuple[str, str]] = []

        def flush() -> None:
            body = "\n".join(buffer).strip("\n")
            buffer.clear()
            if not body:
                return
            if not self.keep_preamble and not headers:
                # Preamble (no header seen yet) is dropped when configured so.
                return
            sections.append((body, self._header_path(headers)))

        fence_char: Optional[str] = None  # current fence char, or None if outside
        fence_len: int = 0                # length of the opening fence run

        for raw_line in text.splitlines():
            if fence_char is not None:
                # Inside a fenced code block: every line is content, but watch
                # for the matching closing fence.
                buffer.append(raw_line)
                close = self._match_fence(raw_line, closing=True)
                if close is not None and close[0] == fence_char \
                        and close[1] >= fence_len:
                    fence_char = None
                    fence_len = 0
                continue
            open_fence = self._match_fence(raw_line, closing=False)
            if open_fence is not None:
                # Entering a fenced code block: the fence line is content, and
                # header detection stays off until the block closes.
                buffer.append(raw_line)
                fence_char = open_fence[0]
                fence_len = open_fence[1]
                continue
            header = self._match_header(raw_line)
            if header is not None:
                # Lines accumulated so far belong to the *previous* context.
                flush()
                level, title = header
                self._push_header(headers, level, title)
            else:
                buffer.append(raw_line)
        flush()
        return sections

    def _match_header(self, line: str) -> Optional[Tuple[int, str]]:
        """Return ``(level, title)`` if ``line`` is a split-able header."""
        match = _HEADER_RE.match(line)
        if not match:
            return None
        level = len(match.group(1))
        if level > self.max_header_level:
            return None
        return level, match.group(2).strip()

    @staticmethod
    def _match_fence(line: str, closing: bool) -> Optional[Tuple[str, int]]:
        """Return ``(fence_char, run_length)`` if ``line`` is a code fence.

        ``closing`` selects the closing-fence rule, which forbids any trailing
        content. The caller verifies that the character matches the opening
        fence and that the run is at least as long. A backtick fence whose
        info string itself contains a backtick is not an opening fence.
        """
        match = (_FENCE_CLOSE_RE if closing else _FENCE_OPEN_RE).match(line)
        if not match:
            return None
        fence = match.group(2)
        char = fence[0]
        if not closing and char == '`' and '`' in match.group(3):
            return None
        return char, len(fence)

    @staticmethod
    def _push_header(headers: Dict[int, str], level: int, title: str) -> None:
        """Open the header at ``level`` and close any deeper open headers."""
        for deeper in [lvl for lvl in headers if lvl >= level]:
            del headers[deeper]
        headers[level] = title

    def _header_path(self, headers: Dict[int, str]) -> str:
        """Join the open headers from shallowest to deepest."""
        if not headers:
            return ""
        return self.path_separator.join(headers[lvl] for lvl in sorted(headers))

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'MarkdownHeaderTextSplitter':
        """Initialize the splitter from its component config."""
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "max_header_level"):
            self.max_header_level = doc_processor_configer.max_header_level
        if hasattr(doc_processor_configer, "header_path_key"):
            self.header_path_key = doc_processor_configer.header_path_key
        if hasattr(doc_processor_configer, "keep_preamble"):
            self.keep_preamble = doc_processor_configer.keep_preamble
        if hasattr(doc_processor_configer, "path_separator"):
            self.path_separator = doc_processor_configer.path_separator
        return self
