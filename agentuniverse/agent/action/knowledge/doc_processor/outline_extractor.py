# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: outline_extractor.py

import re
from typing import Any, Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Longest physical line still considered heading-like for the unmarked
# numbered and CJK forms. ATX/setext lines are exempt from this limit: their
# markers ('#' runs, '===' underlines) are unambiguous.
_MAX_HEADING_LINE = 120

# A candidate title may not end with these characters: a line reading
# "1.5 million units were sold." is prose, not a heading.
_TERMINAL_CHARS = "。．.，,；;：:"

# Whitespace accepted between a marker and its title (ASCII blanks plus the
# fullwidth space U+3000 common in CJK documents).
_SEP = r"[ \t\u3000]"

# ATX heading: 0-3 leading spaces, 1-6 hashes, mandatory blank, title.
_ATX_RE = re.compile(r"^ {0,3}(?P<marks>#{1,6})[ \t]+(?P<title>.+?)[ \t]*$")

# Setext underline: 0-3 leading spaces, then only '=' or only '-'.
_UNDERLINE_RE = re.compile(r"^ {0,3}(?P<marks>=+|-+)[ \t]*$")

# Opening fence of a fenced code block: 0-3 leading spaces, 3+ backticks or
# tildes (an info string may follow backtick fences).
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<marks>`{3,}|~{3,})")

# Fenced-code closer for a fence opened with `char` repeated `length` times.
_FENCE_CLOSE_FMT = r"^ {0,3}%s{%d,}[ \t]*$"

# Arabic numbered heading: "1.", "1.1", "1.1.1." ... followed by a title.
_ARABIC_RE = re.compile(
    r"^ {0,3}(?P<num>\d+(?:\.\d+)*)(?P<dot>\.?)" + _SEP +
    r"+(?P<title>\S.*)$")

# CJK numeral components shared by the marker patterns below.
_CJK_SIMPLE = "一二三四五六七八九十"

# Chinese chapter heading: "第一章", "第12章" ... with an optional title.
_CHAPTER_RE = re.compile(
    r"^ {0,3}(?P<num>第[" + _CJK_SIMPLE + "百千两0-9]+章)" + _SEP +
    r"*(?P<title>.*)$")

# Chinese enumeration heading: "一、" followed by a title. The dun (、)
# itself separates marker from title, so no further blank is required;
# the marker recorded as number includes the dun.
_DUN_RE = re.compile(
    r"^ {0,3}(?P<num>[" + _CJK_SIMPLE + r"]{1,4}、)" + _SEP +
    r"*(?P<title>\S.*)$")

# Chinese sub-enumeration heading: "（一）" (halfwidth parens accepted
# too); likewise no blank required after the closing paren.
_PAREN_RE = re.compile(
    r"^ {0,3}(?P<num>[（(][" + _CJK_SIMPLE + r"]{1,4}[）)])" + _SEP +
    r"*(?P<title>\S.*)$")

# Pattern registry keys used to assign CJK marker depths by first
# occurrence (see OutlineExtractor._scan_cjk).
_CJK_PATTERNS = (
    ("cjk_paren", _PAREN_RE),
    ("cjk_dun", _DUN_RE),
    ("cjk_chapter", _CHAPTER_RE),
)


class OutlineExtractor(DocProcessor):
    """Capture a document's heading hierarchy into metadata.

    Long documents are usually navigated through their headings: a table of
    contents, a chapter/section tree, filter facets. Downstream components
    — splitters that cut at headings, retrievers that boost on section
    titles, UIs that render an outline — all need that structure, yet it is
    exactly the information a plain-text chunk loses first. This processor
    scans each document's text before splitting and stamps the heading
    skeleton into metadata: ``metadata['outline']`` receives one entry per
    heading in document order, each a mapping of ``level`` (normalized
    integer depth, 1-based), ``text`` (the title text, markers stripped),
    ``span`` (``[start, end)`` character offsets into the document text, so
    ``doc.text[span[0]:span[1]] == text`` always holds) and ``number`` (the
    section marker such as ``"1.1"``, ``"一、"`` or ``"第二章"``; ``None``
    for unnumbered Markdown headings). ``metadata['section_count']`` and
    ``metadata['max_depth']`` summarize the outline for quick filtering.

    Recognized heading formats:

    1. Markdown ATX — ``#`` through ``######``; level equals the hash
       count. A closing hash run (``## Title ##``) is stripped; seven or
       more hashes, a missing blank after the hashes, or an empty title is
       not a heading.
    2. Markdown setext — a title line underlined with ``===`` (level 1) or
       ``---`` (level 2). A blank line (or document start) above the
       underline prevents the match, so thematic breaks and YAML front
       matter delimiters alone never become headings.
    3. Arabic numbered sections — ``1.``, ``1.1``, ``1.1.1`` (trailing dot
       optional) followed by title text; level equals the dot depth of the
       number.
    4. CJK numbered sections — ``一、`` / ``（一）`` (halfwidth parens
       accepted) / ``第一章`` (Arabic numerals accepted, as in ``第12章``;
       a bare ``第一章`` with no title is still a heading whose text is
       the marker itself). These markers carry no inherent depth, so the
       k-th distinct marker *form* in document order receives level k — a
       document opening with ``一、`` then ``（一）`` yields levels 1 and 2.

    Mixed documents keep each heading's own rule: an ATX ``###`` is level
    3 regardless of neighboring numbered sections, and vice versa. To keep
    prose from being mistaken for unmarked headings, numbered and CJK
    candidates must be at most 120 characters long and must not end with
    terminal punctuation (``。．.，,；;：:``) — guards that ATX/setext lines
    do not need because their markers are explicit.

    Heading detection never fires inside fenced code blocks (``` or ~~~,
    closing fences honored by character and length), so headings quoted in
    examples survive untouched. The scan is a single pass over the text —
    pure Python, deterministic and offline — and documents are never
    filtered or rewritten: text, id and all pre-existing metadata fields
    are preserved, and the metadata mapping is copied before mutation.

    Stamping rules: a document with at least one heading gets
    ``outline`` / ``section_count`` / ``max_depth`` once it has
    ``min_headings`` headings or more; a document with some headings but
    fewer than ``min_headings`` is left completely untouched, while a
    document with no headings at all always gets an empty outline
    (``section_count`` 0, ``max_depth`` 0) plus a note under
    ``metadata['<outline_key>_note']`` recording that the analysis ran and
    found nothing — useful to distinguish "not yet processed" from
    "processed, no structure".

    Attributes:
        min_headings: Minimum number of headings a document must have for
            the outline to be stamped; must be >= 1. Documents with 1..n-1
            headings are skipped; 0-heading documents always receive the
            empty outline and note.
        outline_key: Metadata key the outline list is written to. The
            companion keys ``section_count`` and ``max_depth`` are fixed.
            An empty value disables all stamping (pass-through mode).
    """

    min_headings: int = 1
    outline_key: str = "outline"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp the heading outline of every document into its metadata.

        Args:
            origin_docs: Documents to analyze, in batch order.
            query: Query object (unused; the outline depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order; text and
            ids are never modified, only metadata is extended.
        """
        for doc in origin_docs:
            outline = self._scan(doc.text or "")
            self._stamp_outline(doc, outline)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Scanning
    # ------------------------------------------------------------------ #

    def _scan(self, text: str) -> List[Dict[str, Any]]:
        """Extract the heading skeleton of one text in document order.

        Args:
            text: Document text ("" for empty/None input).

        Returns:
            List[Dict[str, Any]]: One mapping per heading with keys
            ``level`` (int >= 1), ``text`` (str), ``span`` ([start, end)
            character offsets satisfying ``text[start:end] == text``) and
            ``number`` (str or None).
        """
        headings: List[Dict[str, Any]] = []
        # Depth assigned to each CJK marker form, filled by first
        # occurrence in document order (1, 2, 3, ...).
        cjk_depth: Dict[str, int] = {}
        text = text or ""  # defensive: None behaves like empty text
        # Active fenced-code-block closer (None when not inside a fence).
        fence_close: Optional[re.Pattern] = None
        # Previous line, as a (text, start_offset) pair, when it can still
        # serve as a setext title; None after headings, blank lines and
        # fence lines.
        prev_line: Optional[Tuple[str, int]] = None
        # Index in `headings` of an entry produced by the previous line,
        # so a setext underline can replace a numbered/CJK heading that
        # CommonMark would render as the setext title instead.
        prev_heading_idx: Optional[int] = None

        offset = 0
        for raw_line in text.split("\n"):
            line = raw_line.rstrip("\r")
            start = offset
            offset += len(raw_line) + 1

            if fence_close is not None:
                if fence_close.match(line):
                    fence_close = None
                # Nothing inside a code block can open or close a heading,
                # and its lines cannot become setext titles.
                prev_line = None
                prev_heading_idx = None
                continue

            fence = _FENCE_OPEN_RE.match(line)
            if fence:
                marks = fence.group("marks")
                fence_close = re.compile(
                    _FENCE_CLOSE_FMT % (re.escape(marks[0]), len(marks)))
                prev_line = None
                prev_heading_idx = None
                continue

            heading = self._match_line(line, start, cjk_depth)
            if heading is not None:
                headings.append(heading)
                if heading["number"] is None:
                    # ATX headings are complete one-line blocks: a
                    # following '==='/'---' line is plain text, never a
                    # setext title (matching CommonMark block rules).
                    prev_line = None
                    prev_heading_idx = None
                else:
                    prev_heading_idx = len(headings) - 1
                    prev_line = (line, start)
                continue

            underline = _UNDERLINE_RE.match(line)
            if underline is not None and prev_line is not None:
                # The underline claims the previous line as its title: a
                # numbered/CJK heading recorded from that line is replaced
                # by the setext heading (title text = whole line).
                if prev_heading_idx is not None:
                    headings.pop(prev_heading_idx)
                level = 1 if underline.group("marks")[0] == "=" else 2
                title_line, title_start = prev_line
                title = title_line.strip()
                span = [
                    title_start + (len(title_line) - len(title_line.lstrip())),
                    title_start + len(title_line.rstrip()),
                ]
                headings.append({
                    "level": level,
                    "text": title,
                    "span": span,
                    "number": None,
                })
                prev_line = None
                prev_heading_idx = None
                continue

            if line.strip():
                prev_line = (line, start)
            else:
                prev_line = None
            prev_heading_idx = None

        return headings

    def _match_line(self, line: str, start: int,
                    cjk_depth: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """Try to read one line as a heading outside fenced code blocks.

        ATX lines are always trusted (explicit marker); numbered and CJK
        candidates must pass the length and terminal-punctuation guards.

        Args:
            line: Raw line (carriage returns already stripped).
            start: Character offset of the line inside the document text.
            cjk_depth: Mutable CJK form -> level map, updated in place on
                the first occurrence of each form.

        Returns:
            Optional[Dict[str, Any]]: Heading entry, or None when the line
            is not a heading.
        """
        atx = _ATX_RE.match(line)
        if atx:
            title = atx.group("title").rstrip()
            # Strip a closing hash run ("## Title ##"); a title made of
            # hashes only ("### ###") is an empty heading, not an outline
            # entry.
            if set(title) != {"#"}:
                title = re.sub(r"[ \t]+#+$", "", title)
            if title and set(title) != {"#"}:
                title_start = start + atx.start("title")
                return {
                    "level": len(atx.group("marks")),
                    "text": title,
                    "span": [title_start, title_start + len(title)],
                    "number": None,
                }
            return None

        arabic = _ARABIC_RE.match(line)
        if arabic and self._plausible(line, arabic.group("title")):
            title = arabic.group("title").rstrip()
            number = arabic.group("num")
            title_start = start + arabic.start("title")
            return {
                "level": number.count(".") + 1,
                "text": title,
                "span": [title_start, title_start + len(title)],
                "number": number,
            }

        for key, pattern in _CJK_PATTERNS:
            match = pattern.match(line)
            if not match or not self._plausible(line, match.group("title")):
                continue
            # Only chapter markers stand alone as headings ("第二章"); a
            # bare "一、" or "（一）" without title text is skipped.
            if not match.group("title").rstrip() and key != "cjk_chapter":
                continue
            return self._cjk_heading(match, start, cjk_depth.setdefault(
                key, len(cjk_depth) + 1))
        return None

    @staticmethod
    def _cjk_heading(match: "re.Match", start: int,
                     level: int) -> Dict[str, Any]:
        """Build the outline entry for one CJK numbered heading.

        A bare chapter marker ("第二章") is a legitimate heading on its
        own; in that case the marker doubles as the title text and the
        span covers the marker itself.

        Args:
            match: Regex match of the CJK marker pattern.
            start: Character offset of the line inside the document text.
            level: Depth already assigned to this marker form.

        Returns:
            Dict[str, Any]: Heading entry.
        """
        number = match.group("num")
        title = match.group("title").rstrip()
        if title:
            title_start = start + match.start("title")
        else:
            title = number
            title_start = start + match.start("num")
        return {
            "level": level,
            "text": title,
            "span": [title_start, title_start + len(title)],
            "number": number,
        }

    @staticmethod
    def _plausible(line: str, title: str) -> bool:
        """Apply the anti-false-positive guards of unmarked heading forms.

        Args:
            line: The full candidate line.
            title: The candidate title text (may carry trailing blanks).

        Returns:
            bool: True when the line is short enough to be a heading and
            its title does not end with terminal punctuation.
        """
        if len(line) > _MAX_HEADING_LINE:
            return False
        return not (title.rstrip() and title.rstrip()[-1] in _TERMINAL_CHARS)

    # ------------------------------------------------------------------ #
    # Metadata stamping
    # ------------------------------------------------------------------ #

    def _stamp_outline(self, doc: Document,
                       outline: List[Dict[str, Any]]) -> None:
        """Write the outline results into document metadata.

        The mapping is copied before mutation so a mapping shared with
        other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            outline: Heading entries produced by ``_scan``.
        """
        if not self.outline_key:
            return
        count = len(outline)
        if 0 < count < self.min_headings:
            # Too sparse to be worth an outline: leave the document (and
            # its metadata) completely untouched.
            return
        meta = dict(doc.metadata or {})
        meta[self.outline_key] = outline
        meta["section_count"] = count
        meta["max_depth"] = max((h["level"] for h in outline), default=0)
        if count == 0:
            meta[f"{self.outline_key}_note"] = "no headings detected"
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'OutlineExtractor':
        """Initialize and validate the extractor from component configuration.

        Validation happens eagerly at load time: a silently misconfigured
        extractor stamping under the wrong key would be far harder to
        notice downstream than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            OutlineExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "min_headings") and \
                doc_processor_configer.min_headings is not None:
            min_headings = doc_processor_configer.min_headings
            if isinstance(min_headings, bool) or \
                    not isinstance(min_headings, int):
                raise ValueError("min_headings must be an integer")
            self.min_headings = min_headings
            if self.min_headings < 1:
                raise ValueError("min_headings must be >= 1")

        if hasattr(doc_processor_configer, "outline_key") and \
                doc_processor_configer.outline_key is not None:
            outline_key = doc_processor_configer.outline_key
            if not isinstance(outline_key, str):
                raise ValueError("outline_key must be a string")
            self.outline_key = outline_key

        return self
