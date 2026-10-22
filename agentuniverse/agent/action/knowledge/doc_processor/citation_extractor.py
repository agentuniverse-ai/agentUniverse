# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: citation_extractor.py

import re
from typing import Dict, List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Citation kinds, in canonical sort/lookup order.
KIND_QUOTE = "quote"
KIND_BRACKET = "bracket"
KIND_DOI = "doi"
KIND_ARXIV = "arxiv"
KIND_FOOTNOTE = "footnote"

_KINDS = (KIND_QUOTE, KIND_BRACKET, KIND_DOI, KIND_ARXIV, KIND_FOOTNOTE)
_KIND_RANK = {kind: rank for rank, kind in enumerate(_KINDS)}

# Upper bound on the length of a quoted span, keeping the pairing regexes
# well-behaved on adversarial inputs; real quotations are far shorter.
_MAX_QUOTE_CHARS = 2000

# How far past a closing quotation mark the attribution cues are searched.
_ATTRIBUTION_WINDOW = 80

# Outer quotation styles: curly double, straight double (paired per line)
# and CJK corner brackets.
_QUOTE_DOUBLE_CURLY = re.compile(r"“[^“”]{1,%d}”" % _MAX_QUOTE_CHARS)
_QUOTE_DOUBLE_STRAIGHT = re.compile(r'"[^"\n]{1,%d}"' % _MAX_QUOTE_CHARS)
_QUOTE_CJK = re.compile(r"「[^「」]{1,%d}」" % _MAX_QUOTE_CHARS)

# Inner quotation styles: curly single and CJK white corner brackets. They
# are only reported when they appear OUTSIDE every outer quotation, so a
# quotation nested inside another one is never double-counted.
_QUOTE_INNER_CURLY = re.compile(r"‘[^‘’]{1,%d}’" % _MAX_QUOTE_CHARS)
_QUOTE_INNER_CJK = re.compile(r"『[^『』]{1,%d}』" % _MAX_QUOTE_CHARS)

# Attribution cues searched in the window following a quotation.
_ATTR_CUE_EN = (r"said|says|saying|according to|explains|explained|"
                r"notes|noted|states|stated|writes|wrote|tells|told|"
                r"adds|added")

# English attribution, cue before the speaker: "said Jane Doe",
# "according to the central bank". The speaker phrase is a bounded run of
# word tokens in any case (reports, pronoun-less prose).
_ATTRIBUTION_EN_NAME = re.compile(
    r"\b(" + _ATTR_CUE_EN + r")\s+"
    r"([A-Za-z][\w.'’\-]*(?:\s+[A-Za-z][\w.'’\-]*){0,5})")

# English attribution, pronoun before the cue: "he said", "they noted".
_ATTRIBUTION_EN_PRONOUN = re.compile(
    r"\b(he|she|it|they|we|I)\s+(" + _ATTR_CUE_EN + r")\b")

# Chinese attribution, speaker before the verb: "张三表示", "公司称".
_ATTRIBUTION_ZH = re.compile(r"([\u4e00-\u9fff·]{2,12}?)(表示|认为|指出|说|称)")

# Bracket citation markers: numeric [1] / [12] / [1,2] / [3-5] ...
_BRACKET_NUMERIC = re.compile(
    r"\[\d{1,3}(?:\s*[,;\-–]\s*\d{1,3})*\]")

# Alphanumeric citation keys: [SMITH2026], [Garcia2024a]. A key must start
# with a letter and contain at least one digit, which keeps plain bracketed
# words like [note] or markdown link texts out.
_BRACKET_KEY = re.compile(
    r"\[[A-Za-z][A-Za-z0-9_\-]{0,30}\d[A-Za-z0-9_\-]{0,30}\]")

# Author-year citations: (Author, 2026), (Author et al., 2026a),
# (Wang & Li, 2026), (Smith, Jones and Lee, 2020). The comma before the
# year is required, which keeps prose like "(in 2026)" out.
_AUTHOR_YEAR = re.compile(
    r"\([A-Z][A-Za-z'’\-]+"
    r"(?:(?:\s*(?:,|&)\s*|\s+and\s+)[A-Z][A-Za-z'’\-]+|\s+et\s+al\.?)*"
    r",\s+\d{4}[a-z]?\)")

# DOI markers, both the doi: prefix and the resolver URL form.
_MARKER_DOI = re.compile(
    r"(?:\bdoi\s*:\s*|\bhttps?://(?:dx\.)?doi\.org/)"
    r"10\.\d{4,9}/[^\s\"'<>,;)\]]+",
    re.IGNORECASE)

# arXiv identifiers, both the arXiv: prefix and the abs/pdf URL form.
_MARKER_ARXIV = re.compile(
    r"(?:\barxiv\s*:\s*|\bhttps?://arxiv\.org/(?:abs|pdf)/)"
    r"\d{4}\.\d{4,5}(?:v\d+)?",
    re.IGNORECASE)

# Footnote markers: runs of Unicode superscript digits (¹²³) ...
_FOOTNOTE_SUPERSCRIPT = re.compile(r"[¹²³⁰⁴⁵⁶⁷⁸⁹]+")
# ... and caret-style markers (^1, ^42) not glued to a word character.
_FOOTNOTE_CARET = re.compile(r"\^\d{1,3}(?!\w)")

# Sentence terminators that cut the attribution search window short, so a
# cue in a later sentence is never mistaken for the quotation's source.
_SENTENCE_END = "。．！？!?；;"

# Marker patterns grouped by the citation kind they produce.
_MARKER_PATTERNS = (
    (KIND_BRACKET, (_BRACKET_NUMERIC, _BRACKET_KEY, _AUTHOR_YEAR)),
    (KIND_DOI, (_MARKER_DOI,)),
    (KIND_ARXIV, (_MARKER_ARXIV,)),
    (KIND_FOOTNOTE, (_FOOTNOTE_SUPERSCRIPT, _FOOTNOTE_CARET)),
)


class CitationExtractor(DocProcessor):
    """Find quotations and citation markers and stamp them into metadata.

    Real-world documents carry their evidence in band typography rather
    than in structured fields: reporters quote people inside quotation
    marks, papers lean on numbered or author-year references, datasets are
    pinned by DOIs and arXiv ids, and footnotes trail superscript digits.
    Downstream retrieval can do little with that signal — it is invisible
    to both embeddings and keyword indexes. This processor walks each
    document with pure ``re`` and collects every such marker into
    ``metadata[citations_key]``, giving search and agents something to
    filter, boost or display on.

    Detected kinds:

    * ``quote`` — quoted speech between curly doubles (“…” — shown here as
      plain), straight doubles ("…", paired left to right within a line)
      or CJK corner brackets (「…」). When the text right after the
      closing mark contains an attribution cue — English ``said`` /
      ``according to`` / … or Chinese 表示 / 称 / 说 / … — the cue and its
      speaker phrase are captured into the citation's ``attribution``
      (e.g. ``said Jane Doe`` or ``张三表示``); otherwise it is None.
      Inner quote styles (curly singles ‘…’, CJK 『…』) are only reported
      when they sit outside every outer quotation, so “she said ‘hi’
      today” yields exactly one citation and the nested ‘hi’ is not
      double-counted.
    * ``bracket`` — numeric markers [1], [12], [1,2], [3-5], alphanumeric
      citation keys [SMITH2026], and author-year references (Author,
      2026), (Author et al., 2026a), (Wang & Li, 2026). Bracketed words
      without digits and parenthesised prose stay out.
    * ``doi`` — DOI identifiers, both ``doi:10.xxxx/…`` and
      ``https://doi.org/10.xxxx/…`` forms.
    * ``arxiv`` — arXiv identifiers such as ``arXiv:2507.12345`` and
      ``https://arxiv.org/abs/2507.12345``.
    * ``footnote`` — runs of Unicode superscript digits (¹²³) and
      caret-style markers (^1, ^42).

    Every citation is a mapping
    ``{kind, text, attribution, span}`` where ``text`` is the quotation
    (delimiters included) or the marker exactly as matched,
    ``attribution`` is filled only for quotes, and ``span`` is a
    ``[start, end]`` pair into the document text that reproduces the
    citation's own ``text`` exactly.
    Citations are sorted by document position (then kind, for ties at the
    same position) and capped at ``max_citations``.
    ``metadata[count_key]`` receives a per-kind tally
    (``{quote: n, bracket: n, doi: n, arxiv: n, footnote: n}``, all five
    keys always present, zeros included) computed over the kept list.

    The component is a pass-through: documents are returned unfiltered,
    text and id are never modified, and metadata mappings are copied
    before mutation. The whole pipeline is deterministic, offline and
    dependency-free, which makes it a cheap pre-insertion step before
    chunking — unlike ``AcademicPaperFragmenter``, which re-fragments an
    academic paper by its internal argument structure, this component
    leaves any document format intact and only annotates markers.

    Attributes:
        max_citations: Maximum number of citations kept in the metadata
            list; excess detections are discarded and the per-kind counts
            reflect the kept list. Must be >= 1. Default 100.
        citations_key: Metadata key the citation list is written to; an
            empty value disables that stamp.
        count_key: Metadata key the per-kind count mapping is written to;
            an empty value disables that stamp.
    """

    max_citations: int = 100
    citations_key: str = "citations"
    count_key: str = "citation_count"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp citations and per-kind counts into every document.

        Args:
            origin_docs: Documents to annotate, in batch order.
            query: Query object (unused; extraction depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document list, unfiltered, with
            citation metadata stamped onto each document.
        """
        for doc in origin_docs:
            citations = self._extract(doc.text or "")
            if self.citations_key:
                self._stamp(doc, self.citations_key, citations)
            if self.count_key:
                self._stamp(doc, self.count_key, self._counts(citations))
        return origin_docs

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #

    def _extract(self, text: str) -> List[Dict]:
        """Collect every citation in one text, capped and sorted.

        Args:
            text: Document text (empty string yields no citations).

        Returns:
            List[Dict]: Citation mappings sorted by span, at most
            ``max_citations`` entries.
        """
        found: List[Dict] = []

        # Pass 1: outer quotations. Their spans also fence pass 2.
        outer_spans: List[Tuple[int, int]] = []
        for pattern in (_QUOTE_DOUBLE_CURLY, _QUOTE_DOUBLE_STRAIGHT,
                        _QUOTE_CJK):
            for match in pattern.finditer(text):
                found.append(self._quote_citation(match, text))
                outer_spans.append(match.span())

        # Pass 2: inner-style quotes outside any outer quotation. A quote
        # fully contained in an already-reported outer quotation is the
        # nested-quote case and is deliberately skipped.
        for pattern in (_QUOTE_INNER_CURLY, _QUOTE_INNER_CJK):
            for match in pattern.finditer(text):
                start, end = match.span()
                if any(start >= out_start and end <= out_end
                       for out_start, out_end in outer_spans):
                    continue
                found.append(self._quote_citation(match, text))

        # Pass 3: non-quote markers.
        for kind, patterns in _MARKER_PATTERNS:
            for pattern in patterns:
                for match in pattern.finditer(text):
                    found.append(self._marker_citation(kind, match))

        found.sort(key=lambda c: (c["span"][0], c["span"][1],
                                  _KIND_RANK[c["kind"]]))
        return found[:self.max_citations]

    def _quote_citation(self, match: re.Match, text: str) -> Dict:
        """Build a quote citation, probing for an attribution cue.

        Args:
            match: The quotation match (delimiters included).
            text: The full document text, for the attribution window.

        Returns:
            Dict: Citation mapping for the quotation.
        """
        return {
            "kind": KIND_QUOTE,
            "text": match.group(0),
            "attribution": self._attribution(text, match.end()),
            "span": [match.start(), match.end()],
        }

    @staticmethod
    def _marker_citation(kind: str, match: re.Match) -> Dict:
        """Build a marker citation, trimming trailing DOI punctuation.

        Args:
            kind: Citation kind for the marker.
            match: The marker match.

        Returns:
            Dict: Citation mapping for the marker.
        """
        raw = match.group(0)
        trimmed = raw.rstrip(".,;:")
        end = match.start() + len(trimmed)
        return {
            "kind": kind,
            "text": trimmed,
            "attribution": None,
            "span": [match.start(), end],
        }

    def _attribution(self, text: str, quote_end: int) -> Optional[str]:
        """Find who is responsible for a quotation, if the text says so.

        The window starts right after the closing quotation mark and is
        cut at the first sentence terminator, so cues in a later sentence
        never leak in. Three patterns are tried in a fixed priority
        order; the first hit wins, which keeps the result deterministic.

        Args:
            text: The full document text.
            quote_end: Index just past the closing quotation mark.

        Returns:
            Optional[str]: The attribution phrase (cue plus speaker, or
            speaker plus Chinese verb), or None when no cue is found.
        """
        window = text[quote_end:quote_end + _ATTRIBUTION_WINDOW]
        cut = len(window)
        for idx, char in enumerate(window):
            if char in _SENTENCE_END or (
                    char == "." and (idx + 1 == len(window)
                                     or window[idx + 1].isspace())):
                cut = idx
                break
        window = window[:cut]

        match = _ATTRIBUTION_EN_NAME.search(window)
        if match:
            return f"{match.group(1)} {match.group(2)}".rstrip()
        match = _ATTRIBUTION_EN_PRONOUN.search(window)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        match = _ATTRIBUTION_ZH.search(window)
        if match:
            return match.group(0)
        return None

    @staticmethod
    def _counts(citations: List[Dict]) -> Dict[str, int]:
        """Tally kept citations per kind, all five kinds always present.

        Args:
            citations: The kept citation list.

        Returns:
            Dict[str, int]: Counts keyed by kind in canonical order.
        """
        counts = {kind: 0 for kind in _KINDS}
        for citation in citations:
            counts[citation["kind"]] += 1
        return counts

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
            -> 'CitationExtractor':
        """Initialize and validate the extractor from component configuration.

        Validation happens eagerly at load time: a silently mis-tuned
        extractor (an empty cap, a non-string metadata key) is far easier
        to fix at startup than to notice from polluted metadata later.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            CitationExtractor: The initialized instance.

        Raises:
            ValueError: On an invalid parameter value.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_citations") and \
                doc_processor_configer.max_citations is not None:
            cap = doc_processor_configer.max_citations
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_citations must be an integer")
            self.max_citations = cap
            if self.max_citations < 1:
                raise ValueError("max_citations must be >= 1")

        if hasattr(doc_processor_configer, "citations_key") and \
                doc_processor_configer.citations_key is not None:
            key = doc_processor_configer.citations_key
            if not isinstance(key, str):
                raise ValueError("citations_key must be a string")
            self.citations_key = key

        if hasattr(doc_processor_configer, "count_key") and \
                doc_processor_configer.count_key is not None:
            key = doc_processor_configer.count_key
            if not isinstance(key, str):
                raise ValueError("count_key must be a string")
            self.count_key = key

        return self
