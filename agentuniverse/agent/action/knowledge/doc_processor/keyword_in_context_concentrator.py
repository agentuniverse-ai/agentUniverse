# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: keyword_in_context_concentrator.py

import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Marker prefixed / appended to snippets whose window was cut off by the
# document edge, so a UI can tell a truncated window from a full one.
_ELLIPSIS = '…'

# Runs of whitespace (including newlines and tabs) collapsed to a single
# space inside extracted snippets, so a snippet is always one display line.
_WHITESPACE_RE = re.compile(r'\s+')


class KeywordInContextConcentrator(DocProcessor):
    """Concentrate keyword-in-context (KWIC) snippets into document metadata.

    Retrieval answers "which documents mention the terms?"; it rarely
    preserves *where* or *in what wording* they appear. Downstream
    consumers — evidence snippets in a search UI, citation panels, agents
    that must quote a source precisely — otherwise re-scan full texts at
    display time. This processor pre-computes that concordance work: for
    every occurrence of each keyword it extracts the surrounding
    ``window_size`` characters and stamps the windows into
    ``metadata[kwic_key]``, ready for snippet display without touching the
    document text.

    Keywords come from two sources, merged in a fixed order: the
    component's static ``keywords`` list (config order, deduplicated),
    then — when ``use_query_keywords`` is true and a query is supplied —
    the query's own keyword set, sorted alphabetically so results never
    depend on set iteration order. This makes the component usable at
    both ends of the pipeline: with static domain terms at
    knowledge-insertion time (pre-processing), and with live query terms
    at recall time (post-processing).

    Matching is plain substring search refined with word boundaries
    where they make sense: when a keyword edge is an ASCII word
    character, the match requires that the neighbouring character is
    not another ASCII word character, so ``rate`` matches ``rate`` but
    not ``rates`` or ``generate``; because that boundary only guards
    against ASCII word characters, ``rate`` still matches when glued
    directly to CJK text (``使用rate表示``) — CJK scripts do not
    separate words with spaces, which is also why CJK keyword edges
    carry no boundary at all (``利率`` matches inside ``利率风险``).
    Matching is case-insensitive unless ``case_sensitive``; keywords
    that differ only in case are the same matcher under
    case-insensitive matching and are merged (the first spelling
    wins). Overlapping occurrences of the *same* keyword follow regex
    non-overlapping semantics; different keywords may match the same
    span and are each reported.

    Each snippet records the keyword, its ``start`` / ``end`` offsets in
    the original text, and a display-ready ``context``: the surrounding
    window with whitespace runs collapsed to single spaces and ``…``
    markers where the window was clipped by a document edge. At most
    ``max_snippets`` snippets are stored (in text order), while
    ``total_occurrences`` and the per-keyword ``counts`` always reflect
    every match. Documents with fewer than ``min_occurrences`` matches
    can be dropped entirely (default 0 keeps everything — stamp-only).

    The whole pipeline is pure Python, deterministic and offline; it is
    the inverse of ``JiebaKeywordExtractor`` — that component discovers
    which keywords a document contains, this one zooms in on where
    keywords you already care about occur.

    Attributes:
        keywords: Static keyword list applied to every batch, in config
            order (duplicates and blank entries are dropped; with
            case-insensitive matching, keywords differing only in
            case count as duplicates and keep the first spelling).
        use_query_keywords: When true (default), the query's keyword set
            is merged into the effective keywords (sorted
            alphabetically, after the static list).
        window_size: Characters of context kept on each side of an
            occurrence; 0 narrows the snippet to the keyword itself.
        max_snippets: Maximum snippets stored per document; must be >= 1.
        min_occurrences: Minimum total occurrences for a document to be
            kept; 0 (default) keeps every document (stamp-only).
        case_sensitive: When false (default), keywords match regardless
            of case.
        kwic_key: Metadata key the concordance record is written to on
            kept documents; an empty value disables stamping.
    """

    keywords: List[str] = []
    use_query_keywords: bool = True
    window_size: int = 60
    max_snippets: int = 10
    min_occurrences: int = 0
    case_sensitive: bool = False
    kwic_key: str = "kwic"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp keyword-in-context snippets into each document.

        Args:
            origin_docs: Documents to concentrate, in batch order.
            query: Query object; its keyword set participates when
                ``use_query_keywords`` is true.

        Returns:
            List[Document]: Documents with at least ``min_occurrences``
            keyword occurrences, in batch order, each stamped with its
            concordance record.
        """
        if not origin_docs:
            return []

        effective = self._effective_keywords(query)
        kept: List[Document] = []
        for doc in origin_docs:
            text = doc.text or ""
            occurrences = self._find_occurrences(text, effective)
            if len(occurrences) < self.min_occurrences:
                continue
            if self.kwic_key:
                self._stamp(doc, self.kwic_key,
                            self._build_record(text, effective,
                                               occurrences))
            kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Keyword resolution
    # ------------------------------------------------------------------ #

    def _effective_keywords(self, query: Optional[Query]) -> List[str]:
        """Merge static and query keywords into one ordered, deduplicated
        list.

        Static keywords keep config order; query keywords follow,
        alphabetically sorted — ``Query.keywords`` is a set, and sorting
        keeps the effective list (and therefore all stamped output)
        identical across processes and runs. Under case-insensitive
        matching (the default) keywords that differ only in case are
        the same matcher, so they are merged and only the first
        spelling survives — otherwise every occurrence would be counted
        once per case variant and duplicate spans would crowd the
        snippet list.

        Args:
            query: Query object or None.

        Returns:
            List[str]: Deduplicated, non-empty keywords.
        """
        ordered: List[str] = []
        seen = set()

        def _add(keyword: str) -> None:
            stripped = keyword.strip() if isinstance(keyword, str) else ""
            if not stripped:
                return
            identity = stripped if self.case_sensitive \
                else stripped.lower()
            if identity not in seen:
                seen.add(identity)
                ordered.append(stripped)

        for keyword in self.keywords or []:
            _add(keyword)
        if self.use_query_keywords and query is not None:
            for keyword in sorted(query.keywords or set()):
                _add(keyword)
        return ordered

    # ------------------------------------------------------------------ #
    # Occurrence search
    # ------------------------------------------------------------------ #

    def _find_occurrences(self, text: str,
                          keywords: List[str]) -> List[Tuple[int, int, int]]:
        """Locate every keyword occurrence in the text.

        Args:
            text: Document text.
            keywords: Effective keyword list (index is the tie-breaker
                for the result order).

        Returns:
            List[Tuple[int, int, int]]: ``(start, end, keyword_index)``
            triples sorted by ``(start, end, keyword_index)`` — text
            order first, with earlier-listed keywords winning ties.
        """
        occurrences: List[Tuple[int, int, int]] = []
        flags = 0 if self.case_sensitive else re.IGNORECASE
        for keyword_index, keyword in enumerate(keywords):
            pattern = self._keyword_pattern(keyword, flags)
            for match in pattern.finditer(text):
                occurrences.append(
                    (match.start(), match.end(), keyword_index))
        occurrences.sort()
        return occurrences

    @staticmethod
    def _keyword_pattern(keyword: str, flags: int = 0) -> "re.Pattern[str]":
        """Compile the match pattern for one keyword.

        An ASCII word boundary is required at each keyword edge that is
        an ASCII word character — implemented as lookarounds against
        ``[A-Za-z0-9_]`` rather than ``\\b`` — so short English
        keywords do not fire inside longer words (``rate`` vs
        ``rates`` / ``generate``). ``\\b`` would additionally reject
        keywords glued directly to CJK text (``使用rate表示``), because
        every CJK character is itself a regex word character; the
        lookarounds keep such mixed-script matches working, which is
        the same rationale that exempts CJK keyword edges from any
        boundary at all.

        Args:
            keyword: Non-empty keyword string.
            flags: Regex compilation flags — pass ``re.IGNORECASE``
                for case-insensitive matching (compiled patterns cannot
                receive flags at ``finditer`` time, so the flag must be
                baked in here).

        Returns:
            Compiled pattern honoring the given flags.
        """
        parts = [re.escape(keyword)]
        if KeywordInContextConcentrator._is_ascii_word_char(keyword[0]):
            parts.insert(0, r'(?<![A-Za-z0-9_])')
        if KeywordInContextConcentrator._is_ascii_word_char(keyword[-1]):
            parts.append(r'(?![A-Za-z0-9_])')
        return re.compile(''.join(parts), flags)

    @staticmethod
    def _is_ascii_word_char(char: str) -> bool:
        """Report whether a character is an ASCII word character.

        Args:
            char: Single character.

        Returns:
            bool: True for ``[A-Za-z0-9_]``.
        """
        return char.isascii() and (char.isalnum() or char == '_')

    # ------------------------------------------------------------------ #
    # Record construction
    # ------------------------------------------------------------------ #

    def _build_record(self, text: str, keywords: List[str],
                      occurrences: List[Tuple[int, int, int]]) -> dict:
        """Assemble the concordance record stamped into metadata.

        Args:
            text: Document text (used to slice snippet windows).
            keywords: Effective keyword list.
            occurrences: Sorted ``(start, end, keyword_index)`` triples.

        Returns:
            dict: ``{"keywords", "total_occurrences", "counts",
            "snippets"}``; snippets are capped at ``max_snippets`` while
            the counters cover every occurrence.
        """
        counts = {keyword: 0 for keyword in keywords}
        for _, _, keyword_index in occurrences:
            counts[keywords[keyword_index]] += 1

        snippets = []
        for start, end, keyword_index in occurrences[:self.max_snippets]:
            snippets.append({
                'keyword': keywords[keyword_index],
                'start': start,
                'end': end,
                'context': self._snippet_context(text, start, end),
            })
        return {
            'keywords': list(keywords),
            'total_occurrences': len(occurrences),
            'counts': counts,
            'snippets': snippets,
        }

    def _snippet_context(self, text: str, start: int, end: int) -> str:
        """Extract the display-ready window around one occurrence.

        The window covers ``window_size`` characters on each side of the
        keyword, clipped to the document. Whitespace runs inside the
        window (newlines included) collapse to single spaces — and edge
        whitespace is dropped — so a snippet renders as one line, and an
        ``…`` marker is attached at each edge where the window was cut;
        absence of the marker means the window reaches a real document
        boundary.

        Args:
            text: Document text.
            start: Keyword start offset in the original text.
            end: Keyword end offset in the original text.

        Returns:
            str: Normalized context string with optional ``…`` markers.
        """
        window_start = max(0, start - self.window_size)
        window_end = min(len(text), end + self.window_size)
        context = _WHITESPACE_RE.sub(
            ' ', text[window_start:window_end]).strip()
        if window_start > 0:
            context = _ELLIPSIS + context
        if window_end < len(text):
            context = context + _ELLIPSIS
        return context

    def _stamp(self, doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            key: Metadata key.
            value: Metadata value.
        """
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'KeywordInContextConcentrator':
        """Initialize and validate the concentrator from component
        configuration.

        Validation happens eagerly at load time: a typo like a negative
        window or a zero snippet cap that silently produced empty or
        wrong output would be far harder to notice in production than a
        startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            KeywordInContextConcentrator: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "keywords") and \
                doc_processor_configer.keywords is not None:
            keywords = doc_processor_configer.keywords
            if not isinstance(keywords, (list, tuple)):
                raise ValueError("keywords must be a list of strings")
            for keyword in keywords:
                if not isinstance(keyword, str) or not keyword.strip():
                    raise ValueError(
                        "keywords must be a list of non-empty strings")
            self.keywords = list(keywords)

        if hasattr(doc_processor_configer, "use_query_keywords") and \
                doc_processor_configer.use_query_keywords is not None:
            self.use_query_keywords = bool(
                doc_processor_configer.use_query_keywords)

        if hasattr(doc_processor_configer, "window_size") and \
                doc_processor_configer.window_size is not None:
            window = doc_processor_configer.window_size
            if isinstance(window, bool) or not isinstance(window, int):
                raise ValueError("window_size must be an integer")
            self.window_size = window
            if self.window_size < 0:
                raise ValueError("window_size must be >= 0")

        if hasattr(doc_processor_configer, "max_snippets") and \
                doc_processor_configer.max_snippets is not None:
            limit = doc_processor_configer.max_snippets
            if isinstance(limit, bool) or not isinstance(limit, int):
                raise ValueError("max_snippets must be an integer")
            self.max_snippets = limit
            if self.max_snippets < 1:
                raise ValueError("max_snippets must be >= 1")

        if hasattr(doc_processor_configer, "min_occurrences") and \
                doc_processor_configer.min_occurrences is not None:
            minimum = doc_processor_configer.min_occurrences
            if isinstance(minimum, bool) or not isinstance(minimum, int):
                raise ValueError("min_occurrences must be an integer")
            self.min_occurrences = minimum
            if self.min_occurrences < 0:
                raise ValueError("min_occurrences must be >= 0")

        if hasattr(doc_processor_configer, "case_sensitive") and \
                doc_processor_configer.case_sensitive is not None:
            self.case_sensitive = bool(doc_processor_configer.case_sensitive)

        if hasattr(doc_processor_configer, "kwic_key") and \
                doc_processor_configer.kwic_key is not None:
            key = doc_processor_configer.kwic_key
            if not isinstance(key, str):
                raise ValueError("kwic_key must be a string")
            self.kwic_key = key

        return self
