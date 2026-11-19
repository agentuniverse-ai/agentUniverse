# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: dangling_reference_detector.py

import re
from typing import Dict, List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Reference kinds, each with its own id namespace (figure 3 and table 3 are
# unrelated numbers).
_KINDS = ("figure", "table", "equation")

# Characters that may directly precede a bare parenthesized equation number
# for it to count as a display-equation anchor (ASCII + full-width).
_BARE_EQ_PRECEDING_CHARS = set(".,;:!?=$)") | set("。，；：！？＝）")

# Ordered-list markers stripped when deciding whether a match sits at the
# start of a (markdown) line: "3.", "3)", "a)", "a.".
_ORDERED_MARKER_RE = re.compile(r"\d{1,3}[.)]\s+|[A-Za-z][.)]\s+")

# Markdown block markers: headings, blockquotes, bullets, bold/italic
# markers, horizontal rules — any run of these (plus whitespace) before a
# match still counts as "line-initial".
_BLOCK_MARKER_CHARS = "#>*+- \t"

# Subfigure suffix: "Figure 3a", "Fig. 4(b)", "Figure 3a2" — the letter
# never creates a distinct id, mentions resolve to the base number.
_SUFFIX = r"(?:\(\s*[A-Za-z]\d?\s*\)|[A-Za-z](?![A-Za-z0-9]))"

# Keyword mention patterns. Named groups are fixed across specs:
#   first -> first referenced/defined number
#   tail  -> raw continuation of the mention ("-5", " and 4", ",6")
#   cap   -> optional caption punctuation (":" / "." / full-width colon)
# The trailing (?!\d) keeps "Figure 3.5" from parsing as "Figure 3" plus a
# caption period: the caption group backtracks off the decimal point.
# "and"-joined enumerations ("Figs. 3 and 4") require plural keywords so
# that "Figure 2 and 4 others" stays a single reference; a LaTeX tilde may
# bind keyword and number ("Table~2"); ids are capped at three digits so
# four-digit years ("2020-2025") never parse as references.
_MENTION_SPECS = tuple(
    (kind, re.compile(pattern, flags))
    for kind, pattern, flags in (
        # English figures, plural keywords: "Figures 3-5", "Figs. 3 and 4".
        ("figure",
         r"\b(?:Figures|Figs\.|Figs)[\s~]*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*(?:[-\u2013~]\s*"
         r"(?:\b(?:Figures|Figure|Figs\.|Figs|Fig\.|Fig)[\s~]*)?"
         r"|\s+and\s+)"
         r"\d{1,3}" + _SUFFIX + r"?)*)?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", re.IGNORECASE),
        # English figures, general: "Figure 3", "Fig. 3", "Figure 3-5".
        ("figure",
         r"\b(?:Figures|Figure|Figs\.|Figs|Fig\.|Fig)[\s~]*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*[-\u2013~]\s*"
         r"(?:\b(?:Figures|Figure|Figs\.|Figs|Fig\.|Fig)[\s~]*)?"
         r"\d{1,3}" + _SUFFIX + r"?)*)?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", re.IGNORECASE),
        # English tables, plural keywords: "Tables 2-4", "Tabs. 1 and 2".
        ("table",
         r"\b(?:Tables|Tabs\.|Tabs)[\s~]*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*(?:[-\u2013~]\s*"
         r"(?:\b(?:Tables|Table|Tab\.|Tab)[\s~]*)?"
         r"|\s+and\s+)"
         r"\d{1,3}" + _SUFFIX + r"?)*)?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", re.IGNORECASE),
        # English tables, general: "Table 2", "Tab. 2", "Table 2-4".
        ("table",
         r"\b(?:Tables|Table|Tab\.|Tab)[\s~]*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*[-\u2013~]\s*"
         r"(?:\b(?:Tables|Table|Tab\.|Tab)[\s~]*)?"
         r"\d{1,3}" + _SUFFIX + r"?)*)?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", re.IGNORECASE),
        # English equations, plural keywords: "Eqs. (5) and (6)".
        ("equation",
         r"\b(?:Equations|Eqs\.|Eqs)[\s~]*[(\uff08]?\s*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*[)\uff09]?\s*(?:[-\u2013~]\s*|\s+and\s+)\s*[(\uff08]?\s*"
         r"\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]?)*)?"
         r"\s*[)\uff09]?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", re.IGNORECASE),
        # English equations, general: "Equation (5)", "Eq. 5", "Eq. (5)-(7)".
        ("equation",
         r"\b(?:Equations|Equation|Eqs\.|Eqs|Eq\.|Eq)[\s~]*[(\uff08]?\s*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*[)\uff09]?\s*[-\u2013~]\s*[(\uff08]?\s*"
         r"\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]?)*)?"
         r"\s*[)\uff09]?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", re.IGNORECASE),
        # English equations, parenthesized comma list: "Eqs. (5,6)".
        ("equation",
         r"\b(?:Equations|Equation|Eqs\.|Eqs|Eq\.|Eq)[\s~]*[(\uff08]\s*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*,\s*\d{1,3}" + _SUFFIX + r"?)+)"
         r"\s*[)\uff09]"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", re.IGNORECASE),
        # Chinese figures: "图3", "图 3", "图3至图5", "图3、图4".
        ("figure",
         r"\u56fe[\s~]*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*(?:[-\u2013~\u81f3\u5230]\s*|\u3001\s*)\u56fe?[\s~]*"
         r"\d{1,3}" + _SUFFIX + r"?)*)?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", 0),
        # Chinese tables: "表2", "表 2", "表2-3" ("报表2", "列表3", "图表2"
        # excluded — none of those is a table caption).
        ("table",
         r"(?<![\u62a5\u5217\u56fe])\u8868[\s~]*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*(?:[-\u2013~\u81f3\u5230]\s*|\u3001\s*)\u8868?[\s~]*"
         r"\d{1,3}" + _SUFFIX + r"?)*)?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", 0),
        # Chinese equations: "公式(5)", "方程 5", "公式(5)至(7)", "式(1)和(2)".
        ("equation",
         r"(?:\u516c\u5f0f|\u65b9\u7a0b)[\s~]*[(\uff08]?\s*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*[)\uff09]?\s*(?:[-\u2013~\u81f3\u5230]\s*[(\uff08]?\s*"
         r"\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]?"
         r"|\u3001\s*[(\uff08]?\s*\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]?"
         r"|[\u548c\u53ca\u4e0e]\s*[(\uff08]\s*\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]))*)?"
         r"\s*[)\uff09]?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", 0),
        # Chinese equations, bare "式" form — parentheses required so that
        # words like "格式"/"正式" never match; common binders excluded.
        ("equation",
         r"(?<![\u6b63\u683c\u6a21\u4e66\u5f62\u7248\u65b9])\u5f0f\s*[(\uff08]\s*(?P<first>\d{1,3})" + _SUFFIX + r"?"
         r"(?P<tail>(?:\s*[)\uff09]?\s*(?:[-\u2013~\u81f3\u5230]\s*[(\uff08]?\s*"
         r"\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]?"
         r"|\u3001\s*[(\uff08]?\s*\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]?"
         r"|[\u548c\u53ca\u4e0e]\s*[(\uff08]\s*\d{1,3}" + _SUFFIX + r"?\s*[)\uff09]))*)?"
         r"\s*[)\uff09]?"
         r"(?P<cap>\s*[.:\uff1a])?(?!\d)", 0),
    )
)

# Separator-plus-number pairs parsed out of a mention's tail text; the
# separator decides whether the pair extends a range or joins an
# enumeration.
_TAIL_ELEMENT_RE = re.compile(
    r"([-\u2013~]|\band\b|[,、\u548c\u53ca\u4e0e\u81f3\u5230])"
    r"[\s()\uff08\uff09\u56fe\u8868A-Za-z.]{0,8}(\d{1,3})", re.IGNORECASE)
_RANGE_SEPS = frozenset("-\u2013~\u81f3\u5230")

# Bare display-equation numbers: "(5)" / "（5）" — accepted only when the
# nearest preceding non-whitespace character is punctuation or the tag is
# set off by a wide gap (tab or two-plus spaces, the display-equation
# layout exported from LaTeX/Word) and only whitespace follows on the
# line, which keeps inline numeric citations out.
_BARE_EQ_RE = re.compile(r"[(\uff08]\s*(\d{1,3})\s*[)\uff09]")


class DanglingReferenceDetector(DocProcessor):
    """Flag references to figures/tables/equations with no matching anchor.

    Knowledge QA over ingested documents breaks quietly when a chunk says
    "see Figure 3" but the document never defines Figure 3 — the anchor was
    dropped by an export, sits in another chunk, or the numbering is simply
    wrong. Retrieval then confidently returns text pointing at evidence the
    reader will never find. This processor scans every document's text for
    two kinds of occurrences in three id namespaces (figure / table /
    equation) and reports references whose target was never defined:

    - **Anchors** — patterns that *define* a numbered item: caption lines
      such as "Figure 3: ...", "Fig. 3. ...", "Table 2: ...", "图3：...",
      "表2：...", display equations "Equation (5):", "Eq. (5)." and bare
      line-final equation numbers like "y = f(x)   (5)". An anchor must sit
      at the start of a line (markdown block markers and ordered-list
      markers in between are tolerated) or directly after a ``**`` bold
      marker, and must be followed by caption punctuation (``:`` ``.``
      full-width colon). A mention missing either property is a reference.
      A ranged caption ("Figures 3-5: ...") anchors every id it covers.
    - **References** — in-text mentions such as "see Figure 3", "as shown
      in Fig. 3", "Table 2 lists", "by Eq. (5)", "如图3所示", "见表2".
      Ranges expand: "Figures 3-5" references figures 3, 4 and 5 (and
      "图3至图5" likewise); enumerations list their members: "Figs. 3 and
      4", "Eqs. (5,6)", "图3、图4".

    Every referenced id without an anchor of the same kind is reported as a
    dangling reference; every anchored id that is never referenced is
    reported as unreferenced (informational only — unreferenced anchors do
    not affect the overall verdict). Findings land in document metadata:

    - ``metadata['dangling_references']`` — list of ``{kind, id, span,
      context}`` entries (span is ``[start, end)`` in the raw text, context
      holds ``context_chars`` characters on each side), capped at
      ``max_report`` entries;
    - ``metadata['dangling_count']`` — total dangling occurrences (never
      capped);
    - ``metadata['unreferenced_anchors']`` / ``metadata
      ['unreferenced_anchor_count']`` — same shape for anchors no reference
      points at (list capped, count full);
    - ``metadata['reference_integrity']`` — ``'ok'`` when nothing dangles,
      ``'dangling'`` otherwise.

    The position rule resolves the classic ambiguity of a caption that
    repeats its own number: in "Figure 3: the architecture. As Figure 3
    shows, ..." the line-initial "Figure 3:" is an anchor while the
    mid-sentence "Figure 3" is a reference, so the document is judged
    sound. Conversely "This is depicted in Figure 3." stays a reference:
    its trailing period is sentence punctuation, not caption punctuation,
    because the mention is not line-initial.

    The detector is deliberately conservative: bare parenthesized numbers
    only anchor equations at end of line after punctuation or a wide gap,
    "Figure 3.5" parses as a reference to figure 3 rather than an anchor
    with a decimal caption, and Chinese "表2" is ignored inside "报表2",
    "列表3" and "图表2" (list/chart words, not tables). Subfigure suffixes
    resolve to the base id — "see Figure 3a" and "Fig. 4(b)" reference
    figures 3 and 4, a "Figure 3a:" caption anchors figure 3 — the letter
    never creates a distinct id. English keywords match case-insensitively
    ("eq. (5)", "FIG. 3") and a LaTeX tilde binds keyword and number
    ("Table~2"). Ids are capped at three digits so four-digit years
    ("2020-2025") never parse as references. It is pure Python
    (regex only), fully offline and deterministic — suited to broken-doc QA
    at knowledge-ingestion time, before chunking or embedding spend. It
    complements citation cataloging components such as CitationExtractor:
    those record what a document cites, while this one checks that internal
    figure/table/evidence pointers resolve. Documents are never filtered
    or modified — text, id and existing metadata values are untouched, and
    metadata mappings are copied before new keys are written.

    Attributes:
        max_report: Maximum number of entries kept in the
            'dangling_references' and 'unreferenced_anchors' lists; the
            count fields always carry full totals. 0 disables both lists.
            Must be >= 0.
        context_chars: Number of context characters kept on each side of a
            dangling reference span. Must be >= 0.
        max_range_span: Maximum number of ids a range mention ("Figures
            3-5") expands to; longer ranges are clamped to this many ids
            starting at the lower bound. Must be >= 1.
        include_unreferenced: When true (default) unreferenced anchors are
            collected; they never affect 'reference_integrity'.
        dangling_key: Metadata key for the dangling reference list; an
            empty value disables that list ('dangling_count' is always
            written).
        unreferenced_key: Metadata key for the unreferenced anchor list; an
            empty value disables that list ('unreferenced_anchor_count' is
            always written).
        integrity_key: Metadata key for the 'ok' | 'dangling' verdict; an
            empty value disables the verdict.
    """

    max_report: int = 30
    context_chars: int = 30
    max_range_span: int = 50
    include_unreferenced: bool = True
    dangling_key: str = "dangling_references"
    unreferenced_key: str = "unreferenced_anchors"
    integrity_key: str = "reference_integrity"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Analyze every document and stamp reference-integrity metadata.

        Args:
            origin_docs: Documents to scan, in batch order.
            query: Query object (unused; the analysis depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order, each
            stamped with dangling-reference findings in its metadata.
        """
        for doc in origin_docs:
            text = doc.text or ""
            anchors, references = self._scan(text)
            self._stamp_findings(doc, text, anchors, references)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Scanning
    # ------------------------------------------------------------------ #

    def _scan(self, text: str) -> Tuple[dict, List[dict]]:
        """Collect anchors and references from one text.

        Args:
            text: Raw document text.

        Returns:
            tuple: ``(anchors, references)`` where ``anchors`` maps every
            kind to ``{id: (start, end)}`` of its first defining anchor and
            ``references`` is a list of ``{kind, id, span}`` dicts in text
            order (ranges and enumerations contribute one entry per id, all
            sharing the mention's span).
        """
        anchors = {kind: {} for kind in _KINDS}
        references: List[dict] = []

        # One pass over every spec; overlapping candidates (e.g. "公式(5)"
        # matching both the 公式 and the bare 式 pattern, the plural and
        # general figure specs on the same mention, or a bare "(5)" inside
        # "Eq. (5)") are resolved in favor of the match that starts
        # earliest, longest first.
        candidates = []
        for kind, regex in _MENTION_SPECS:
            for match in regex.finditer(text):
                candidates.append((match.start(), -match.end(), kind, match))
        for match in _BARE_EQ_RE.finditer(text):
            if self._is_bare_equation_anchor(text, match.start(),
                                             match.end()):
                candidates.append((match.start(), -match.end(),
                                   "equation", match))
        # Earliest start first, longer match wins ties; the kind and match
        # never participate in the comparison.
        candidates.sort(key=lambda item: (item[0], item[1]))

        claimed: List[Tuple[int, int]] = []
        max_claimed_end = -1
        for start, neg_end, kind, match in candidates:
            end = -neg_end
            if start >= max_claimed_end:
                claimed = []
                max_claimed_end = -1
            else:
                claimed = [span for span in claimed if span[1] > start]
                if any(c_start < end for c_start, _ in claimed):
                    continue
                max_claimed_end = max((span[1] for span in claimed),
                                      default=-1)
            claimed.append((start, end))
            max_claimed_end = max(max_claimed_end, end)

            if match.re is _BARE_EQ_RE:
                anchors["equation"].setdefault(int(match.group(1)),
                                               (start, end))
                continue

            ids = self._mention_ids(int(match.group("first")),
                                    match.group("tail"))
            has_caption = match.group("cap") is not None

            # Anchor rule: caption punctuation AND line-initial (or after
            # a bold marker). A ranged or enumerated caption ("Figures
            # 3-5: ...") anchors every id it covers.
            if has_caption and self._at_anchor_position(text, start):
                for number in ids:
                    anchors[kind].setdefault(number, (start, end))
            else:
                for number in ids:
                    references.append(
                        {"kind": kind, "id": number, "span": (start, end)})

        return anchors, references

    def _at_anchor_position(self, text: str, position: int) -> bool:
        """Decide whether a mention at ``position`` sits in anchor position.

        True when the mention starts a line (ignoring markdown block
        markers such as ``#``, ``>``, ``*``, ``-``, ordered-list markers
        and leading whitespace) or directly follows a ``**`` bold marker
        ("**Figure 3.** caption" style).

        Args:
            text: Raw document text.
            position: Match start offset.

        Returns:
            bool: True when the position qualifies as anchor position.
        """
        line_start = text.rfind("\n", 0, position) + 1
        prefix = text[line_start:position]
        if prefix.endswith("**"):
            return True
        index = 0
        while index < len(prefix):
            while index < len(prefix) and \
                    prefix[index] in _BLOCK_MARKER_CHARS:
                index += 1
            if index >= len(prefix):
                break
            marker = _ORDERED_MARKER_RE.match(prefix, index)
            if marker and marker.group(0).strip() != "":
                index = marker.end()
                continue
            break
        return index >= len(prefix)

    @staticmethod
    def _is_bare_equation_anchor(text: str, start: int, end: int) -> bool:
        """Check the conservative conditions for a bare "(5)" equation id.

        The nearest non-whitespace character before the match must be
        punctuation (period, comma, semicolon, colon, ``=``, ``$`` or a
        closing parenthesis — ASCII or full-width) or the tag must be set
        off from the formula by a wide gap (a tab or two-plus spaces, the
        centered display-equation layout), and only whitespace may follow
        on the line. This keeps inline numeric citations "(5)" mid-sentence
        and parenthesized formula operands like "n(9)" out.

        Args:
            text: Raw document text.
            start: Match start offset.
            end: Match end offset.

        Returns:
            bool: True when the match qualifies as an equation anchor.
        """
        prefix = text[:start]
        stripped = prefix.rstrip()
        gap = prefix[len(stripped):]
        before_punct = bool(stripped) and \
            stripped[-1] in _BARE_EQ_PRECEDING_CHARS
        wide_gap = "\t" in gap or len(gap) >= 2
        if not (before_punct or wide_gap):
            return False
        after = text[end:]
        newline = after.find("\n")
        rest = after if newline == -1 else after[:newline]
        return rest.strip() == ""

    def _mention_ids(self, first: int, tail: str) -> List[int]:
        """Expand a mention into every referenced id.

        A missing, inverted ("Figures 5-3") or clamped range degrades
        gracefully: an inverted range keeps only the first id, and ranges
        longer than ``max_range_span`` ids are clamped to that many ids
        from the lower bound, which keeps a stray "Figures 1-999" from
        flooding the report. Enumeration separators ("and", "," and the
        Chinese enumeration comma) contribute their numbers as-is instead
        of spanning the interval.

        Args:
            first: First (or only) referenced number.
            tail: Raw continuation text from the mention's tail group,
                empty for a single-number mention.

        Returns:
            List[int]: The referenced ids in mention order.
        """
        ids = [first]
        if not tail:
            return ids
        last = first
        for sep, number in _TAIL_ELEMENT_RE.findall(tail):
            number = int(number)
            if sep in _RANGE_SEPS:
                if number > last:
                    budget = self.max_range_span - len(ids)
                    if budget > 0:
                        ids.extend(
                            range(last + 1, min(number, last + budget) + 1))
                    last = number
            elif number not in ids:
                ids.append(number)
                last = number
        return ids

    # ------------------------------------------------------------------ #
    # Reporting
    # ------------------------------------------------------------------ #

    def _stamp_findings(self, doc: Document, text: str, anchors: dict,
                        references: List[dict]) -> None:
        """Compute and stamp dangling-reference findings into metadata.

        Args:
            doc: Document whose metadata receives the findings.
            text: The document's raw text (for context windows).
            anchors: Kind -> {id: anchor span} mapping from ``_scan``.
            references: Reference entries from ``_scan``.
        """
        dangling: List[dict] = []
        referenced_ids = {kind: set() for kind in _KINDS}
        for entry in references:
            referenced_ids[entry["kind"]].add(entry["id"])
            if entry["id"] not in anchors[entry["kind"]]:
                start, end = entry["span"]
                dangling.append({
                    "kind": entry["kind"],
                    "id": entry["id"],
                    "span": [start, end],
                    "context": text[max(0, start - self.context_chars):
                                    min(len(text), end + self.context_chars)],
                })

        unreferenced: List[dict] = []
        for kind in _KINDS:
            for number, span in sorted(anchors[kind].items()):
                if number not in referenced_ids[kind]:
                    unreferenced.append(
                        {"kind": kind, "id": number,
                         "span": [span[0], span[1]]})

        findings = {
            "dangling_count": len(dangling),
            "unreferenced_anchor_count": len(unreferenced),
        }
        if self.integrity_key:
            findings[self.integrity_key] = \
                "dangling" if dangling else "ok"
        if self.dangling_key and self.max_report > 0:
            findings[self.dangling_key] = dangling[:self.max_report]
        if self.unreferenced_key and self.include_unreferenced and \
                self.max_report > 0:
            findings[self.unreferenced_key] = unreferenced[:self.max_report]
        self._stamp(doc, findings)

    def _stamp(self, doc: Document, findings: dict) -> None:
        """Write findings into document metadata via a copied mapping.

        The metadata mapping is copied before mutation so a mapping shared
        with other pipeline stages never observes surprising in-place
        edits; text, id and existing metadata values are never touched.

        Args:
            doc: Document to stamp.
            findings: Mapping of metadata keys to findings.
        """
        meta = dict(doc.metadata or {})
        meta.update(findings)
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'DanglingReferenceDetector':
        """Initialize and validate the detector from component configuration.

        Validation happens eagerly at load time: a misconfigured detector
        that silently reported nothing would be far harder to notice in
        production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            DanglingReferenceDetector: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_report") and \
                doc_processor_configer.max_report is not None:
            value = doc_processor_configer.max_report
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("max_report must be an integer")
            self.max_report = value
            if self.max_report < 0:
                raise ValueError("max_report must be >= 0")

        if hasattr(doc_processor_configer, "context_chars") and \
                doc_processor_configer.context_chars is not None:
            value = doc_processor_configer.context_chars
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("context_chars must be an integer")
            self.context_chars = value
            if self.context_chars < 0:
                raise ValueError("context_chars must be >= 0")

        if hasattr(doc_processor_configer, "max_range_span") and \
                doc_processor_configer.max_range_span is not None:
            value = doc_processor_configer.max_range_span
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("max_range_span must be an integer")
            self.max_range_span = value
            if self.max_range_span < 1:
                raise ValueError("max_range_span must be >= 1")

        if hasattr(doc_processor_configer, "include_unreferenced") and \
                doc_processor_configer.include_unreferenced is not None:
            self.include_unreferenced = bool(
                doc_processor_configer.include_unreferenced)

        for attr in ("dangling_key", "unreferenced_key", "integrity_key"):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                value = getattr(doc_processor_configer, attr)
                if not isinstance(value, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, value)

        return self
