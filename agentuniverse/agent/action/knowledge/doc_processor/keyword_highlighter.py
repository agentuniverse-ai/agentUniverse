# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: keyword_highlighter.py

"""
Keyword highlighting pre-processor.

Rewrites each document's text with highlight markers wrapped around every
occurrence of the configured keywords, so a RAG front-end that renders the
stored chunk can show the user *where in the source text* the query terms
sit. It is the *annotation* direction of issue #258 (knowledge
pre-processing) and complements ``KeywordInContextConcentrator`` (#3512):
that component copies keyword context windows into metadata while leaving
the source text untouched, whereas this one modifies the text itself.

Matching is regex-based, deterministic and dependency-free: keywords are
``re.escape``d (never interpreted as patterns), compared case-insensitively
unless ``case_sensitive``, and — under the default ``whole_words`` —
guarded by ASCII word boundaries so ``new`` matches inside ``a new deal``
but not inside ``renewal``. Word boundaries are deliberately ASCII-only:
CJK text carries no spaces, so a CJK keyword is inherently whole-word and
must match mid-string (``模型`` inside ``大模型时代``). Overlapping
keywords are resolved longest-first: with both ``new`` and ``New York``
configured, the phrase wins where they overlap and the shorter term still
matches elsewhere.

``max_highlights`` caps how many occurrences carry markers (default 200);
further matches are left unmarked while ``metadata['highlight_count']``
still reports the total. Every document is stamped with that total plus
``metadata['highlighted_keywords']``, the unique configured keywords that
actually matched.

Re-running the processor on its own output is a no-op: matches already
adjacent to the marker pair are recognized and skipped, so markers are
never doubled.
"""

import re
from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

# Preset marker styles: configuration name -> (prefix, suffix).
MARKER_STYLES = {
    "bold": ("**", "**"),            # Markdown bold.
    "mark": ("==", "=="),            # Obsidian/Highlight.js style mark.
    "wiki": ("[[", "]]"),            # Wiki link / double bracket.
    "html": ("<mark>", "</mark>"),   # HTML mark element.
}

# Characters that count as word characters for the ASCII word boundary.
_ASCII_WORD_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")

# Metadata keys stamped on every processed document.
_COUNT_KEY = "highlight_count"
_KEYWORDS_KEY = "highlighted_keywords"


class KeywordHighlighter(DocProcessor):
    """Wrap configured keyword occurrences in the document text with markers.

    Text modification is the point of this component: unlike extractors that
    only stamp metadata, the rewritten ``doc.text`` is what a downstream
    renderer displays, with every match visibly delimited. Because markers
    change the text, a chunk processed here should be embedded *after*
    highlighting only if the embedding model tolerates the marker syntax —
    the typical placement is at pre-display time or on a display copy.

    Matching semantics:

    - every keyword is escaped with ``re.escape``; keywords are literals,
      never regular expressions;
    - ``case_sensitive: false`` (default) folds case for both sides;
    - ``whole_words: true`` (default) adds ASCII word boundaries around a
      keyword whose edge character is an ASCII word character — ``new``
      does not match inside ``renewal`` or ``Newfoundland``. Keywords with
      non-ASCII edges (CJK in particular) match without boundaries: CJK
      scripts carry no spaces, so an occurrence is inherently whole-word;
    - overlapping keywords resolve longest-first: with ``new`` and
      ``New York`` both configured, ``New York`` wins where they overlap
      and ``new`` still matches standalone occurrences;
    - ``max_highlights`` (default 200) bounds the number of occurrences
      carrying markers; matches beyond the cap are left unmarked while
      the count still reflects every match found.

    Idempotence: a match already wrapped in the configured marker pair
    (i.e. produced by an earlier run of this component with the same
    style) is recognized and skipped, so processing a document twice does
    not double the markers and leaves both text and stamped metadata
    unchanged. Repeated runs with *different* marker styles are not
    protected against and are not recommended.

    Attributes:
        keywords: Non-empty list of literal keywords to highlight.
            Surrounding whitespace is stripped at load time.
        marker: Marker style — ``bold`` (``**kw**``), ``mark``
            (``==kw==``), ``wiki`` (``[[kw]]``), ``html``
            (``<mark>kw</mark>``) or ``custom`` (use ``marker_prefix`` /
            ``marker_suffix``).
        marker_prefix: Opening marker, used only when ``marker`` is
            ``custom``.
        marker_suffix: Closing marker, used only when ``marker`` is
            ``custom``.
        case_sensitive: When true, matching distinguishes case. Default
            false.
        whole_words: When true (default), ASCII word boundaries are
            required around keywords with ASCII word-character edges.
        max_highlights: Maximum number of occurrences carrying markers per
            document; must be >= 1. Default 200.
    """

    keywords: List[str] = []
    marker: str = "bold"
    marker_prefix: str = ""
    marker_suffix: str = ""
    case_sensitive: bool = False
    whole_words: bool = True
    max_highlights: int = 200

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Insert highlight markers around keyword matches in each document.

        Args:
            origin_docs: Documents whose text should be annotated.
            query: Query object (unused; the keyword set comes from
                configuration, so highlighting is query-independent and
                stable across recalls).

        Returns:
            List[Document]: The same documents with matches wrapped in the
            configured markers and per-document ``highlight_count`` /
            ``highlighted_keywords`` stamped into their metadata.
        """
        pattern = self._compiled_pattern() if self._normalized_keywords() else None
        prefix, suffix = self._markers()
        for doc in origin_docs:
            text = doc.text or ""
            if pattern is None:
                new_text, count, matched = text, 0, []
            else:
                new_text, count, matched = self._highlight(text, pattern,
                                                           prefix, suffix)
            if new_text != text:
                doc.text = new_text
            metadata = dict(doc.metadata or {})
            metadata[_COUNT_KEY] = count
            metadata[_KEYWORDS_KEY] = matched
            doc.metadata = metadata
        return origin_docs

    # ------------------------------------------------------------------ #
    # Highlighting core
    # ------------------------------------------------------------------ #

    def _highlight(self, text: str, pattern: "re.Pattern", prefix: str,
                   suffix: str) -> Tuple[str, int, List[str]]:
        """Insert markers around every eligible match in one text.

        Args:
            text: Document text.
            pattern: Compiled alternation of all keyword patterns.
            prefix: Opening marker.
            suffix: Closing marker.

        Returns:
            Tuple[str, int, List[str]]: The rewritten text, the total
            number of matches found (including already-marked and
            beyond-cap ones), and the unique configured keywords that
            matched, in first-occurrence order.
        """
        keywords = self._normalized_keywords()
        pieces: List[str] = []
        matched: List[str] = []
        total = 0
        marked = 0
        last = 0
        for m in pattern.finditer(text):
            keyword = keywords[int(m.lastgroup[1:])]
            if keyword not in matched:
                matched.append(keyword)
            total += 1
            # Skip guard: a match already wrapped in the marker pair comes
            # from an earlier pass of this component. It counts toward the
            # cap (it does carry markers) but is never wrapped again, which
            # is what makes a second pass a no-op.
            if self._carries_markers(text, m.start(), m.end(), prefix, suffix):
                if marked < self.max_highlights:
                    marked += 1
                continue
            if marked >= self.max_highlights:
                continue
            marked += 1
            pieces.append(text[last:m.start()])
            pieces.append(prefix + m.group(0) + suffix)
            last = m.end()
        pieces.append(text[last:])
        return "".join(pieces), total, matched

    @staticmethod
    def _carries_markers(text: str, start: int, end: int, prefix: str,
                         suffix: str) -> bool:
        """Check whether a match is already wrapped in the marker pair.

        Args:
            text: The text being scanned (possibly output of an earlier
                highlighting pass).
            start: Match start offset.
            end: Match end offset.
            prefix: Opening marker.
            suffix: Closing marker.

        Returns:
            bool: True when the marker pair sits exactly around the match.
        """
        return (start >= len(prefix) and end + len(suffix) <= len(text)
                and text[start - len(prefix):start] == prefix
                and text[end:end + len(suffix)] == suffix)

    # ------------------------------------------------------------------ #
    # Pattern construction
    # ------------------------------------------------------------------ #

    def _normalized_keywords(self) -> List[str]:
        """Return deduplicated keywords, longest first.

        Case-insensitive duplicates (e.g. ``New`` and ``new``) collapse to
        their first configured spelling. Longest-first ordering makes the
        regex alternation prefer the longer keyword wherever two overlap,
        which is the documented overlap policy.

        Returns:
            List[str]: Unique keywords sorted by descending length.
        """
        seen = set()
        unique: List[str] = []
        for keyword in self.keywords:
            keyword = keyword.strip() if isinstance(keyword, str) else keyword
            if not keyword:
                continue
            folded = keyword if self.case_sensitive else keyword.casefold()
            if folded in seen:
                continue
            seen.add(folded)
            unique.append(keyword)
        return sorted(unique, key=lambda kw: (-len(kw), kw))

    def _compiled_pattern(self) -> "re.Pattern":
        """Compile the combined keyword alternation.

        Each keyword becomes one named group ``kN`` (so ``m.lastgroup``
        maps a match back to its configured keyword), escaped with
        ``re.escape`` and — under ``whole_words`` — fenced with ASCII
        word-boundary lookarounds on the edges where the keyword itself
        starts or ends with an ASCII word character.

        Returns:
            re.Pattern: Compiled case-(in)sensitive alternation.

        Raises:
            ValueError: If no usable keyword remains after validation.
        """
        parts = [self._keyword_pattern(keyword, index)
                 for index, keyword in enumerate(self._normalized_keywords())]
        if not parts:
            raise ValueError(
                "keywords must contain at least one non-empty keyword")
        flags = 0 if self.case_sensitive else re.IGNORECASE
        return re.compile("|".join(parts), flags)

    def _keyword_pattern(self, keyword: str, index: int) -> str:
        """Build the regex fragment for one keyword.

        Args:
            keyword: Literal keyword, already stripped and non-empty.
            index: Keyword position, used for the named group.

        Returns:
            str: A named group matching this keyword with optional ASCII
            word-boundary fences.
        """
        pattern = re.escape(keyword)
        if self.whole_words:
            if keyword[0] in _ASCII_WORD_CHARS:
                pattern = r"(?<![A-Za-z0-9_])" + pattern
            if keyword[-1] in _ASCII_WORD_CHARS:
                pattern = pattern + r"(?![A-Za-z0-9_])"
        return f"(?P<k{index}>{pattern})"

    def _markers(self) -> Tuple[str, str]:
        """Resolve the configured style to an (prefix, suffix) pair.

        Returns:
            Tuple[str, str]: Opening and closing marker strings.
        """
        if self.marker == "custom":
            return self.marker_prefix, self.marker_suffix
        return MARKER_STYLES[self.marker]

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'KeywordHighlighter':
        """Initialize and validate the highlighter from component
        configuration.

        Validation happens eagerly at load time: a highlighter silently
        matching nothing (empty keywords, unknown style, blank custom
        markers) would be far harder to notice than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            KeywordHighlighter: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "keywords") and \
                doc_processor_configer.keywords is not None:
            self.keywords = doc_processor_configer.keywords

        if hasattr(doc_processor_configer, "marker") and \
                doc_processor_configer.marker is not None:
            self.marker = doc_processor_configer.marker
            if self.marker not in MARKER_STYLES and self.marker != "custom":
                raise ValueError(
                    "marker must be one of "
                    f"{sorted(MARKER_STYLES)} or 'custom', got "
                    f"'{self.marker}'")

        if hasattr(doc_processor_configer, "marker_prefix") and \
                doc_processor_configer.marker_prefix is not None:
            self.marker_prefix = doc_processor_configer.marker_prefix
        if hasattr(doc_processor_configer, "marker_suffix") and \
                doc_processor_configer.marker_suffix is not None:
            self.marker_suffix = doc_processor_configer.marker_suffix
        if self.marker == "custom":
            if not isinstance(self.marker_prefix, str) or \
                    not self.marker_prefix:
                raise ValueError(
                    "marker_prefix must be a non-empty string when marker "
                    "is 'custom'")
            if not isinstance(self.marker_suffix, str) or \
                    not self.marker_suffix:
                raise ValueError(
                    "marker_suffix must be a non-empty string when marker "
                    "is 'custom'")

        if hasattr(doc_processor_configer, "case_sensitive") and \
                doc_processor_configer.case_sensitive is not None:
            self.case_sensitive = bool(doc_processor_configer.case_sensitive)

        if hasattr(doc_processor_configer, "whole_words") and \
                doc_processor_configer.whole_words is not None:
            self.whole_words = bool(doc_processor_configer.whole_words)

        if hasattr(doc_processor_configer, "max_highlights") and \
                doc_processor_configer.max_highlights is not None:
            cap = doc_processor_configer.max_highlights
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_highlights must be an integer")
            self.max_highlights = cap
            if self.max_highlights < 1:
                raise ValueError("max_highlights must be >= 1")

        # Validate keywords last so style errors surface first; strip
        # surrounding whitespace, then require at least one usable entry.
        if not isinstance(self.keywords, (list, tuple)):
            raise ValueError(
                "keywords must be a list of non-empty strings, got "
                f"{type(self.keywords).__name__}")
        cleaned: List[str] = []
        for keyword in self.keywords:
            if not isinstance(keyword, str):
                raise ValueError(
                    f"each keyword must be a string, got {keyword!r}")
            stripped = keyword.strip()
            if not stripped:
                raise ValueError(
                    "keywords must not contain empty or whitespace-only "
                    f"entries, got {keyword!r}")
            cleaned.append(stripped)
        if not cleaned:
            raise ValueError(
                "keywords must contain at least one non-empty keyword")
        self.keywords = cleaned

        return self
