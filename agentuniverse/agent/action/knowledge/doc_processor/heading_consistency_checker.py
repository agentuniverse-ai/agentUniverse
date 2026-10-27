# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: heading_consistency_checker.py

import re
from typing import List, Optional, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# ATX heading: up to three leading spaces, one to six hashes, then either
# end of line or at least one space/tab before the title text. '#' followed
# directly by a non-space character (e.g. '#5 bolts') and runs of more than
# six hashes are not headings, matching the CommonMark family of rules.
_ATX_HEADING = re.compile(r'^( {0,3})(#{1,6})(?:[ \t]+(?P<title>.*?))?[ \t]*$')

# Optional ATX closing sequence: a run of hashes at the end of the title,
# separated from it by at least one space/tab ('## Title ##').
_CLOSING_SEQUENCE = re.compile(r'[ \t]+#+[ \t]*$')

# Fenced code block openers: three or more backticks or tildes after up to
# three leading spaces. Everything until the matching close fence is code.
_FENCE_OPEN = re.compile(r'^ {0,3}(?P<marker>`{3,}|~{3,})')

# Fenced code block closers: same fence character, at least as many
# repetitions as the opener, nothing else on the line but whitespace.
_FENCE_CLOSE = re.compile(r'^ {0,3}(`{3,}|~{3,})[ \t]*$')

# Findings cap kept in metadata so a pathological document cannot blow up
# the stored payload; full counts always survive in the totals.
_DEFAULT_MAX_FINDINGS = 100


class HeadingConsistencyChecker(DocProcessor):
    """Validate ATX heading structure and stamp findings into metadata.

    Documentation corpora enter knowledge bases through many hands —
    exports, conversions, concatenated chapters — and heading structure is
    usually the first casualty: levels jump from h1 straight to h4, the
    same section title appears three times, an outline entry is left
    blank. Downstream splitters and outline consumers trust this structure
    silently. This processor is the ingestion QA gate: it parses the ATX
    headings of every document (immune to fenced code blocks, where lines
    like ``#include`` must never count) and records every structural
    problem it finds into document metadata, leaving text and document
    order untouched. It complements ``OutlineExtractor``: that component
    *extracts* the outline silently, this one *validates* it.

    Five checks run over the parsed heading sequence, each producing a
    finding ``{kind, line, text, detail}``:

    1. ``level_jump`` — a heading more than one level deeper than the
       previous one (h1 followed by h4 skips three levels). Skipping
       exactly one level is the normal nesting step and never flagged;
       jumping back up any number of levels is always allowed. This check
       is informational and style-guide-dependent in the way linters are:
       flagging a jump is a hint for a human, not an error.
    2. ``duplicate_heading`` — the same title text (casefolded, internal
       whitespace collapsed) appearing two or more times. One finding per
       duplicated title, anchored at the first occurrence and listing
       every occurrence line in ``detail``; empty headings are excluded
       (they get their own check). Title text is compared regardless of
       level, since outline consumers navigate by title.
    3. ``empty_heading`` — a heading marker with no title text after the
       hashes (``##`` on its own), which renders as a nameless outline
       entry. A bare closing sequence (``## ##``) also leaves no text.
    4. ``max_depth_exceeded`` — a heading deeper than ``max_level``. The
       default 6 disables the check (six being the deepest ATX level), so
       it only fires when a style guide configures a tighter bound.
    5. ``first_heading_not_h1`` — the document's first heading starts at
       level 2 or deeper (common after a title page is stripped). Off by
       default because many valid documents legitimately start at h2.

    Findings land in metadata together with summary numbers:
    ``metadata[issues_key]`` is the finding list capped at
    ``max_findings`` entries (default 100, document order); ``metadata
    [counts_key]`` counts findings per kind over the *complete* result;
    ``metadata[total_key]`` is the uncapped total; and ``metadata
    [score_key]`` is a crude health heuristic — 1.0 for a clean document,
    minus 0.1 per finding, floored at 0.0. The score is deliberately
    simple: it orders documents by how much heading surgery they need, it
    does not weigh severities. A document containing no headings at all
    has nothing to validate and receives a score of ``None`` with an empty
    finding list, so callers can distinguish 'nothing to check' from
    'checked and clean'.

    Only ATX headings (``#`` to ``######``) are recognized, up to three
    leading spaces; setext underlines are not parsed. The whole pipeline
    is pure Python, deterministic and offline; documents pass through
    unchanged apart from the metadata stamps, so the component can safely
    sit in front of filters that drop documents by score.

    Attributes:
        max_level: Deepest allowed ATX level, in [1, 6]. The default 6
            turns ``max_depth_exceeded`` off — ATX itself stops at 6, so
            nothing can exceed it until a tighter bound is configured.
        flag_first_not_h1: When true, report the first heading starting at
            level 2 or deeper as ``first_heading_not_h1``; default false.
        max_findings: Maximum number of findings kept in the metadata
            list, >= 1. Counts, total and score always reflect every
            finding, capped list or not.
        issues_key: Metadata key the capped finding list is written to;
            an empty value disables that stamp.
        counts_key: Metadata key the per-kind counts are written to; an
            empty value disables that stamp.
        total_key: Metadata key the uncapped finding total is written to;
            an empty value disables that stamp.
        score_key: Metadata key the heading score is written to; an empty
            value disables that stamp.
    """

    max_level: int = 6
    flag_first_not_h1: bool = False
    max_findings: int = _DEFAULT_MAX_FINDINGS
    issues_key: str = "heading_issues"
    counts_key: str = "heading_issue_counts"
    total_key: str = "heading_issue_total"
    score_key: str = "heading_score"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Validate heading structure of every document, in place of metadata.

        Args:
            origin_docs: Documents to validate; each is analyzed
                independently, so heading-level tracking never leaks
                across documents.
            query: Query object (unused; validation depends only on the
                documents' own text).

        Returns:
            List[Document]: The same document objects in the same order,
            each stamped with heading findings, counts and score.
        """
        for doc in origin_docs or []:
            headings = self._parse_headings(doc.text or "")
            findings = self._check_headings(headings)
            counts = {}
            for finding in findings:
                counts[finding["kind"]] = counts.get(finding["kind"], 0) + 1
            total = len(findings)
            self._stamp(doc, self.issues_key, findings[:self.max_findings])
            self._stamp(doc, self.counts_key, counts)
            self._stamp(doc, self.total_key, total)
            # No headings means nothing was validated — None keeps that
            # distinct from a checked-and-clean 1.0.
            self._stamp(doc, self.score_key,
                        self._score(total) if headings else None)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Heading extraction
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_headings(text: str) -> List[Tuple[int, str, int]]:
        """Extract ATX headings as (level, title, line) tuples.

        Lines inside fenced code blocks are skipped, so a ``#include``
        inside a C snippet or a ``## comment`` inside a shell transcript
        never pollutes the outline. A fence opens with three or more
        backticks or tildes and closes on a later line repeating the same
        character at least as many times; fence lines themselves are code,
        not headings. A title's optional closing hash run and surrounding
        whitespace are stripped ('## Title ##' -> 'Title'); a title left
        as nothing but hashes ('## ##') counts as an empty heading.

        Args:
            text: Document text (None treated as empty).

        Returns:
            List[Tuple[int, str, int]]: Headings in document order.
        """
        headings: List[Tuple[int, str, int]] = []
        fence_char = ""
        fence_len = 0
        for line_no, line in enumerate((text or "").splitlines(), start=1):
            if fence_char:
                close = _FENCE_CLOSE.match(line)
                if close and close.group(1)[0] == fence_char and \
                        len(close.group(1)) >= fence_len:
                    fence_char = ""
                continue
            fence = _FENCE_OPEN.match(line)
            if fence:
                marker = fence.group("marker")
                fence_char = marker[0]
                fence_len = len(marker)
                continue
            heading = _ATX_HEADING.match(line)
            if heading:
                level = len(heading.group(2))
                title = heading.group("title") or ""
                title = _CLOSING_SEQUENCE.sub("", title).strip()
                # A title left as nothing but hashes ('## ##' or '## #') is
                # a bare closing sequence, i.e. an empty heading.
                if not title.strip("#"):
                    title = ""
                headings.append((level, title, line_no))
        return headings

    # ------------------------------------------------------------------ #
    # Consistency checks
    # ------------------------------------------------------------------ #

    def _check_headings(self, headings: List[Tuple[int, str, int]]) \
            -> List[dict]:
        """Run all heading checks over one document's heading sequence.

        Args:
            headings: Parsed headings as (level, title, line) tuples, in
                document order; an empty sequence yields no findings.

        Returns:
            List[dict]: Findings as ``{kind, line, text, detail}``,
            sorted by line number; findings on the same line keep check
            order (first-heading, per-heading, duplicates).
        """
        if not headings:
            return []

        findings: List[dict] = []

        if self.flag_first_not_h1 and headings[0][0] > 1:
            level, title, line = headings[0]
            findings.append({
                "kind": "first_heading_not_h1",
                "line": line,
                "text": title,
                "detail": f"document starts at level {level} instead of 1",
            })

        previous_level = 0
        for level, title, line in headings:
            if not title:
                findings.append({
                    "kind": "empty_heading",
                    "line": line,
                    "text": "",
                    "detail": "no text after the hashes",
                })
            if previous_level and level - previous_level > 1:
                findings.append({
                    "kind": "level_jump",
                    "line": line,
                    "text": title,
                    "detail": f"level jumps from {previous_level} to "
                              f"{level} (skip {level - previous_level})",
                })
            if level > self.max_level:
                findings.append({
                    "kind": "max_depth_exceeded",
                    "line": line,
                    "text": title,
                    "detail": f"level {level} exceeds max_level "
                              f"{self.max_level}",
                })
            previous_level = level

        # Duplicate titles: grouped by casefolded, whitespace-collapsed
        # text; groups keep first-seen order so output is deterministic.
        # Empty headings are skipped — they are already reported as
        # empty_heading and 'blank' would otherwise collapse them all.
        occurrences = {}
        for level, title, line in headings:
            if not title:
                continue
            key = " ".join(title.casefold().split())
            occurrences.setdefault(key, []).append((title, line))
        for group in occurrences.values():
            if len(group) < 2:
                continue
            first_title, first_line = group[0]
            lines = ", ".join(str(line) for _, line in group)
            findings.append({
                "kind": "duplicate_heading",
                "line": first_line,
                "text": first_title,
                "detail": f"appears {len(group)} times at line(s) {lines}",
            })

        findings.sort(key=lambda finding: finding["line"])
        return findings

    # ------------------------------------------------------------------ #
    # Scoring and metadata helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _score(total: int) -> float:
        """Score a document from its finding total.

        1.0 for a clean document, 0.1 deducted per finding, floored at
        0.0. Computed in integer tenths so the result never carries
        floating-point noise. The value is a deliberately simple ranking
        heuristic, not a weighted severity assessment; documents without
        any headings never reach this method — they receive a score of
        None from the caller instead.

        Args:
            total: Total number of findings (uncapped).

        Returns:
            float: Score in [0.0, 1.0].
        """
        return max(0, 10 - total) / 10

    def _stamp(self, doc: Document, key: str, value) -> None:
        """Write one entry into document metadata via a copied mapping.

        Empty keys disable the stamp, and the metadata mapping is copied
        before mutation so a mapping shared with other pipeline stages
        never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            key: Metadata key; empty disables stamping.
            value: Metadata value.
        """
        if not key:
            return
        meta = dict(doc.metadata or {})
        meta[key] = value
        doc.metadata = meta

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'HeadingConsistencyChecker':
        """Initialize and validate the checker from component configuration.

        Validation happens eagerly at load time: a misconfigured checker
        that silently skipped a check would be far harder to notice in
        production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            HeadingConsistencyChecker: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "max_level") and \
                doc_processor_configer.max_level is not None:
            level = doc_processor_configer.max_level
            if isinstance(level, bool) or not isinstance(level, int):
                raise ValueError("max_level must be an integer")
            self.max_level = level
            if not 1 <= self.max_level <= 6:
                raise ValueError("max_level must be in [1, 6]")

        if hasattr(doc_processor_configer, "flag_first_not_h1") and \
                doc_processor_configer.flag_first_not_h1 is not None:
            self.flag_first_not_h1 = \
                bool(doc_processor_configer.flag_first_not_h1)

        if hasattr(doc_processor_configer, "max_findings") and \
                doc_processor_configer.max_findings is not None:
            cap = doc_processor_configer.max_findings
            if isinstance(cap, bool) or not isinstance(cap, int):
                raise ValueError("max_findings must be an integer")
            self.max_findings = cap
            if self.max_findings < 1:
                raise ValueError("max_findings must be >= 1")

        for attr in ("issues_key", "counts_key", "total_key", "score_key"):
            if hasattr(doc_processor_configer, attr) and \
                    getattr(doc_processor_configer, attr) is not None:
                key = getattr(doc_processor_configer, attr)
                if not isinstance(key, str):
                    raise ValueError(f"{attr} must be a string")
                setattr(self, attr, key)

        return self
