# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: section_role_classifier.py

"""
Section role classifier.

Classifies the sections of each input :class:`Document` by their scholarly
role — ``intro`` / ``method`` / ``results`` / ``discussion`` / ``conclusion``
(plus the non-core ``abstract`` / ``references`` / ``acknowledgments`` /
``other``) — and stamps the classification into the document's *metadata*
without altering its text. This is the knowledge *pre-processing* direction
of issue #258: once roles are recorded, downstream academic QA routing can
send a query about the experimental setup to ``method`` sections, a query
about numbers to ``results`` sections, and so on, instead of retrieving
against the whole paper uniformly.

The component is pure-Python (standard library only), deterministic, and
offline: the same input always yields the same metadata — no timestamps, no
randomness, no network, no model calls.

Sections are delimited by markdown ATX headings (``#`` … ``######``); heading
detection is fence-immune, so a ``# comment`` line inside a fenced code block
is never mistaken for a section title (same heading and fence rules as the
built-in ``MarkdownHeaderTextSplitter``).

Role assignment uses two mechanisms:

1. **Keyword match (high confidence).** The heading text is matched
   case-insensitively against ordered keyword families. When a heading
   matches several families (e.g. ``Results and Discussion``), the
   first-listed family wins — the precedence order is ``intro`` >
   ``method`` > ``results`` > ``discussion`` > ``conclusion`` >
   ``abstract`` > ``references`` > ``acknowledgments``. This mirrors the
   reading order of a paper, so compound headings resolve to the role a
   reader would cite the section by.
2. **Positional fallback (low confidence).** Headings with no keyword match
   are classified by position: the first section of the document becomes
   ``intro`` and the last becomes ``conclusion``; unmatched sections in the
   middle become ``other``. Fallback can be disabled via configuration.

A document with no headings at all is passed through unmodified, with a note
recorded in its metadata.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

# ATX heading: 1-6 leading '#', mandatory whitespace, then the title text. A
# trailing run of '#' (closed ATX syntax) and surrounding whitespace are
# stripped. A line such as "#no-space" or "####### seven" is not a heading.
# These patterns mirror the built-in MarkdownHeaderTextSplitter so both
# components agree on what counts as a section boundary.
_HEADER_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")

# Fenced code blocks (CommonMark). An opening fence is up to three leading
# spaces followed by three or more backticks or tildes; a backtick fence may
# not carry a backtick in its info string. A closing fence is up to three
# leading spaces, the same fence character repeated at least as many times as
# the opening fence, then only trailing whitespace. While inside a fence,
# heading detection is suppressed so a '# Example' line inside a ```python
# block is treated as code instead of a section title.
_FENCE_OPEN_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})[ \t]*$")

# Ordered role keyword families. Match is a case-insensitive substring test
# on the heading text; the family order is the multi-match precedence order
# (first listed wins). English keywords are given in their stem form where a
# shorter entry subsumes longer ones ("result" also matches "results",
# "conclusion" also matches "conclusions", "method" also matches "methods"
# and "methodology"). "related work" is listed under both intro (primary —
# a related-work section is introductory context) and references (secondary
# — only reachable if a future family reordering puts references first).
_ROLE_KEYWORDS: List[Tuple[str, List[str]]] = [
    ('intro', ['introduction', 'intro', 'background', 'related work',
               '引言', '背景']),
    ('method', ['method', 'methods', 'methodology', 'approach',
                'experimental setup', 'materials', '方法', '实验']),
    ('results', ['result', 'results', 'evaluation', 'findings', 'analysis',
                 '结果', '分析']),
    ('discussion', ['discussion', 'limitations', '威胁']),
    ('conclusion', ['conclusion', 'conclusions', 'summary', 'future work',
                    '结论', '总结']),
    ('abstract', ['abstract', '摘要']),
    ('references', ['references', 'bibliography', '参考文献',
                    'related work']),
    ('acknowledgments', ['acknowledg']),
]

# The four core IMRaD roles; ``has_imrad`` is True when all are present.
_IMRAD_ROLES = ('intro', 'method', 'results', 'conclusion')

# Confidence labels: 'high' for keyword matches, 'low' for positional ones.
_CONFIDENCE_HIGH = 'high'
_CONFIDENCE_LOW = 'low'

# Metadata keys stamped by this processor.
KEY_SECTION_ROLES = 'section_roles'
KEY_ROLE_COUNTS = 'role_counts'
KEY_HAS_IMRAD = 'has_imrad'
KEY_NOTE = 'section_roles_note'

_NO_HEADINGS_NOTE = 'No ATX headings detected; document passed through unmodified.'


class SectionRoleClassifier(DocProcessor):
    """Classify document sections by scholarly role into metadata.

    Attributes:
        max_sections (int): Maximum number of section records kept in
            ``metadata['section_roles']``; further sections are still counted
            in ``role_counts`` / ``has_imrad`` but not listed. Must be >= 1.
        positional_fallback (bool): When True, the first unmatched section is
            classified ``intro`` and the last ``conclusion`` with low
            confidence; when False, unmatched sections are all ``other``.
    """

    max_sections: int = 30
    positional_fallback: bool = True

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp section-role metadata into each document.

        Args:
            origin_docs (List[Document]): Documents whose ``text`` is parsed
                as markdown. Document text and existing metadata are
                preserved; only the classification keys are added.
            query (Query, optional): Unused; kept for interface compatibility.

        Returns:
            List[Document]: The input documents, each carrying
            ``section_roles`` (capped), ``role_counts`` (all sections) and
            ``has_imrad`` in its metadata. An empty input yields an empty
            list.
        """
        if not origin_docs:
            return []
        for doc in origin_docs:
            self._classify_document(doc)
        return origin_docs

    def _classify_document(self, doc: Document) -> None:
        """Classify one document and stamp the results into its metadata."""
        sections = self._extract_sections(doc.text or '')
        if doc.metadata is None:
            doc.metadata = {}

        if not sections:
            doc.metadata[KEY_SECTION_ROLES] = []
            doc.metadata[KEY_ROLE_COUNTS] = {}
            doc.metadata[KEY_HAS_IMRAD] = False
            doc.metadata[KEY_NOTE] = _NO_HEADINGS_NOTE
            return

        role_counts: Dict[str, int] = {}
        records: List[Dict[str, Any]] = []
        total = len(sections)
        for index, (level, heading, span, para_count) in enumerate(sections):
            role, confidence = self._classify_heading(
                heading,
                first=(index == 0),
                last=(index == total - 1),
            )
            role_counts[role] = role_counts.get(role, 0) + 1
            records.append({
                'heading': heading,
                'level': level,
                'role': role,
                'confidence': confidence,
                'span': span,
                'para_count': para_count,
            })

        doc.metadata[KEY_SECTION_ROLES] = records[:self.max_sections]
        doc.metadata[KEY_ROLE_COUNTS] = role_counts
        doc.metadata[KEY_HAS_IMRAD] = all(
            role_counts.get(role, 0) > 0 for role in _IMRAD_ROLES)

    # ------------------------------------------------------------------ #
    # Section extraction (pure) — fully testable offline
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_sections(text: str) -> List[Tuple[int, str, List[int], int]]:
        """Split ``text`` into heading-delimited sections.

        Returns a list of ``(level, heading, span, para_count)`` tuples in
        document order. ``span`` is ``[start, end)`` in characters from the
        start of the heading line through the last line before the next
        heading (or end of text). ``para_count`` counts blocks of non-blank
        body lines separated by blank lines. Content before the first
        heading (preamble) is not a section. Lines inside fenced code blocks
        are never treated as headings.
        """
        sections: List[Tuple[int, str, List[int], int]] = []
        fence_char: Optional[str] = None
        fence_len = 0
        current: Optional[Dict[str, Any]] = None

        offset = 0
        for raw_line in text.splitlines(keepends=True):
            line = raw_line.rstrip('\r\n')
            start = offset
            offset += len(raw_line)
            if offset > len(text):
                offset = len(text)

            if fence_char is not None:
                close = _FENCE_CLOSE_RE.match(line)
                if close is not None and close.group(2)[0] == fence_char \
                        and len(close.group(2)) >= fence_len:
                    fence_char = None
                    fence_len = 0
                SectionRoleClassifier._consume(current, line)
                continue

            open_fence = _FENCE_OPEN_RE.match(line)
            if open_fence is not None:
                fence = open_fence.group(2)
                if not (fence[0] == '`' and '`' in open_fence.group(3)):
                    # A backtick fence may not carry a backtick in its info
                    # string; otherwise such a line is ordinary content.
                    fence_char = fence[0]
                    fence_len = len(fence)
                    SectionRoleClassifier._consume(current, line)
                    continue

            header = _HEADER_RE.match(line)
            if header is not None:
                if current is not None:
                    current['span'][1] = start
                    sections.append(SectionRoleClassifier._finish(current))
                level = len(header.group(1))
                heading = header.group(2).strip()
                current = {'level': level, 'heading': heading,
                           'span': [start, offset], 'paras': 0,
                           'in_block': False}
            else:
                SectionRoleClassifier._consume(current, line)

        if current is not None:
            current['span'][1] = offset
            sections.append(SectionRoleClassifier._finish(current))
        return sections

    @staticmethod
    def _consume(current: Optional[Dict[str, Any]], line: str) -> None:
        """Account for one body line inside the open section, if any."""
        if current is None:
            return
        if line.strip():
            if not current['in_block']:
                current['paras'] += 1
                current['in_block'] = True
        else:
            current['in_block'] = False

    @staticmethod
    def _finish(current: Dict[str, Any]) -> Tuple[int, str, List[int], int]:
        """Freeze the open section as a ``(level, heading, span, paras)`` tuple."""
        return (current['level'], current['heading'],
                [current['span'][0], current['span'][1]], current['paras'])

    # ------------------------------------------------------------------ #
    # Role classification (pure)
    # ------------------------------------------------------------------ #

    def _classify_heading(self, heading: str, first: bool, last: bool) \
            -> Tuple[str, str]:
        """Return ``(role, confidence)`` for one section heading.

        Keyword families are consulted in precedence order; the first family
        with a (case-insensitive) substring hit wins, with high confidence.
        Unmatched headings fall back to position (first -> ``intro``, last ->
        ``conclusion``) with low confidence; middle sections (and all
        unmatched sections when ``positional_fallback`` is disabled) become
        ``other``.
        """
        lowered = heading.lower()
        for role, keywords in _ROLE_KEYWORDS:
            if any(keyword in lowered for keyword in keywords):
                return role, _CONFIDENCE_HIGH
        if self.positional_fallback:
            if first:
                return 'intro', _CONFIDENCE_LOW
            if last:
                return 'conclusion', _CONFIDENCE_LOW
        return 'other', _CONFIDENCE_LOW

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'SectionRoleClassifier':
        """Initialize the classifier from its component config.

        Raises:
            ValueError: If ``max_sections`` is not a positive integer or
                ``positional_fallback`` is not a boolean.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "max_sections"):
            self.max_sections = doc_processor_configer.max_sections
        if hasattr(doc_processor_configer, "positional_fallback"):
            self.positional_fallback = \
                doc_processor_configer.positional_fallback
        self._validate_config()
        return self

    def _validate_config(self) -> None:
        """Validate configuration attribute types and ranges."""
        if not isinstance(self.max_sections, int) or isinstance(
                self.max_sections, bool) or self.max_sections < 1:
            raise ValueError(
                f"max_sections must be a positive integer, "
                f"got {self.max_sections!r}")
        if not isinstance(self.positional_fallback, bool):
            raise ValueError(
                f"positional_fallback must be a boolean, "
                f"got {self.positional_fallback!r}")
