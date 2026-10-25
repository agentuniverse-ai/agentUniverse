# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: paragraph_stats_profiler.py

import re
import statistics
from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Line terminators recognized when grouping text into paragraphs: the
# Unix LF, the Windows CRLF pair and the legacy bare CR. Exotic Unicode
# boundaries (\v, \f, \u2028, ...) are deliberately NOT terminators here.
_LINE_BREAK_RE = re.compile(r"\r\n|\r|\n")


class ParagraphStatsProfiler(DocProcessor):
    """Profile paragraph-level structure statistics into document metadata.

    Knowledge-ingestion QA needs cheap signals that answer "is the shape of
    this text what we expected?" before anything expensive runs on it. A
    PDF-to-text converter that swallowed every paragraph break, a crawler
    that dumped an entire chapter as one wall of text, or a formatter that
    shattered a document into one-line fragments all look identical to a
    content-quality scorer yet poison chunking downstream. This processor
    examines only the STRUCTURE of each document — how the text is laid out
    in paragraphs — and stamps the measurements into metadata. It is the
    structural counterpart of content-oriented scorers: it never judges
    what the text says, only how it is paragraphed, and it never modifies
    the text itself.

    Paragraph model, stated precisely:

    - the text is cut into lines on `\r\n`, `\r` or `\n` (CRLF documents
      behave exactly like LF ones);
    - a line is blank when it contains only whitespace;
    - a paragraph is a maximal run of consecutive non-blank lines — runs of
      one OR MORE blank lines all separate paragraphs equally (a single
      blank line is already a boundary), while single line breaks inside a
      run stay INSIDE the paragraph (soft-wrapped prose is one paragraph,
      not many);
    - each paragraph is trimmed to its first and last non-whitespace
      character; its length counts every character between them — internal
      single line breaks and inner spacing included — and its span records
      those bounds as character offsets into the original text, so
      ``text[start:end]`` reproduces the paragraph exactly. Leading and
      trailing blank lines yield no paragraph; whitespace-only text has
      none.

    Reported in ``metadata[stats_key]``: ``paragraph_count``,
    ``char_count`` (total across paragraphs), ``mean_paragraph_chars``,
    ``median_paragraph_chars``, ``max_paragraph_chars``,
    ``min_paragraph_chars``, ``longest_paragraph_span`` (``{"start", "end"}``
    of the first longest paragraph, else None),
    ``single_line_paragraph_count`` (paragraphs without an internal line
    break), ``long_paragraph_count`` (paragraphs longer than
    ``long_threshold``, default 2000 chars) and ``short_paragraph_count``
    (paragraphs shorter than ``short_threshold``, default 20 chars).
    ``metadata[flag_key]`` carries a one-word verdict:

    - ``long_paragraphs`` — more than ``long_ratio`` (default 0.5) of the
      total paragraph text sits in over-long paragraphs;
    - ``fragmented`` — more than ``fragmented_ratio`` (default 0.7) of the
      paragraphs are under the short threshold;
    - ``mixed`` — both conditions; ``none`` — neither.

    Everything is computed with the standard library only: deterministic
    (stable sorting, first-longest tie-break, float statistics), offline
    and dependency-free. Documents are never dropped, reordered or edited;
    metadata mappings are copied before mutation, and empty statistics
    keep stable numeric types (0 / 0.0, span None) so downstream consumers
    need no special-casing.

    Attributes:
        long_threshold: Paragraph length above which a paragraph counts
            as suspiciously long; integer >= 1, default 2000.
        short_threshold: Paragraph length below which a non-empty
            paragraph counts as suspiciously short; integer >= 0,
            default 20.
        long_ratio: Fraction of total paragraph characters that must sit
            in long paragraphs (strictly more) to raise the
            ``long_paragraphs`` flag; in [0, 1], default 0.5.
        fragmented_ratio: Fraction of paragraphs that must be short
            (strictly more) to raise the ``fragmented`` flag; in [0, 1],
            default 0.7.
        stats_key: Metadata key the statistics dict is written to; an
            empty value disables stamping.
        flag_key: Metadata key the structure flag is written to; an empty
            value disables stamping.
    """

    long_threshold: int = 2000
    short_threshold: int = 20
    long_ratio: float = 0.5
    fragmented_ratio: float = 0.7
    stats_key: str = "paragraph_stats"
    flag_key: str = "structure_flag"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Stamp paragraph structure statistics into every document.

        Args:
            origin_docs: Documents to profile, in batch order.
            query: Query object (unused; profiling depends only on the
                documents' own text).

        Returns:
            List[Document]: The same documents in the same order — none
            is dropped, reordered or edited; each carries the statistics
            in its metadata.
        """
        for doc in origin_docs:
            stats, flag = self._profile(doc.text or "")
            if self.stats_key:
                self._stamp(doc, self.stats_key, stats)
            if self.flag_key:
                self._stamp(doc, self.flag_key, flag)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Structure analysis helpers
    # ------------------------------------------------------------------ #

    def _profile(self, text: str) -> Tuple[dict, str]:
        """Compute the statistics dict and the structure flag of one text.

        Args:
            text: Document text (None already coerced to "").

        Returns:
            Tuple[dict, str]: (statistics, flag) where flag is one of
            'none', 'long_paragraphs', 'fragmented', 'mixed'.
        """
        paragraphs = self._paragraphs(text or "")
        lengths = [p[2] for p in paragraphs]
        total = sum(lengths)

        if paragraphs:
            # max() keeps the FIRST paragraph on ties, so the span is
            # a deterministic function of the text alone.
            longest = max(paragraphs, key=lambda p: p[2])
            stats = {
                "paragraph_count": len(paragraphs),
                "char_count": total,
                "mean_paragraph_chars": float(statistics.mean(lengths)),
                "median_paragraph_chars":
                    float(statistics.median(lengths)),
                "max_paragraph_chars": max(lengths),
                "min_paragraph_chars": min(lengths),
                "longest_paragraph_span":
                    {"start": longest[0], "end": longest[1]},
                "single_line_paragraph_count":
                    sum(1 for p in paragraphs if p[3]),
                "long_paragraph_count":
                    sum(1 for n in lengths if n > self.long_threshold),
                "short_paragraph_count":
                    sum(1 for n in lengths if n < self.short_threshold),
            }
            long_chars = sum(n for n in lengths
                             if n > self.long_threshold)
            long_flagged = long_chars / total > self.long_ratio
            fragmented = (stats["short_paragraph_count"] /
                          len(paragraphs)) > self.fragmented_ratio
        else:
            stats = {
                "paragraph_count": 0,
                "char_count": 0,
                "mean_paragraph_chars": 0.0,
                "median_paragraph_chars": 0.0,
                "max_paragraph_chars": 0,
                "min_paragraph_chars": 0,
                "longest_paragraph_span": None,
                "single_line_paragraph_count": 0,
                "long_paragraph_count": 0,
                "short_paragraph_count": 0,
            }
            long_flagged = False
            fragmented = False

        if long_flagged and fragmented:
            flag = "mixed"
        elif long_flagged:
            flag = "long_paragraphs"
        elif fragmented:
            flag = "fragmented"
        else:
            flag = "none"
        return stats, flag

    @staticmethod
    def _paragraphs(text: str) -> List[Tuple[int, int, int, bool]]:
        """Split text into paragraphs on runs of blank lines.

        Args:
            text: Raw document text.

        Returns:
            List[Tuple[int, int, int, bool]]: One tuple per paragraph —
            (start, end, chars, single_line) where [start, end) are
            character offsets into ``text`` trimmed to the first/last
            non-whitespace character, ``chars`` is ``end - start`` and
            ``single_line`` marks paragraphs without an internal line
            break. Empty for text without any non-blank line.
        """
        # Line spans in the original text: walk every terminator so each
        # line keeps its exact offsets (the terminator itself belongs to
        # neither line).
        line_spans = []
        start = 0
        for match in _LINE_BREAK_RE.finditer(text):
            line_spans.append((start, match.start()))
            start = match.end()
        line_spans.append((start, len(text)))

        paragraphs = []
        run_start = run_end = None
        run_lines = 0
        for line_start, line_end in line_spans:
            if text[line_start:line_end].strip():
                if run_start is None:
                    run_start, run_end, run_lines = line_start, line_end, 1
                else:
                    run_end = line_end
                    run_lines += 1
            elif run_start is not None:
                paragraphs.append(
                    ParagraphStatsProfiler._trimmed_span(
                        text, run_start, run_end, run_lines))
                run_start = None
        if run_start is not None:
            paragraphs.append(
                ParagraphStatsProfiler._trimmed_span(
                    text, run_start, run_end, run_lines))
        return paragraphs

    @staticmethod
    def _trimmed_span(text: str, start: int, end: int,
                      lines: int) -> Tuple[int, int, int, bool]:
        """Trim a paragraph run to its non-whitespace bounds.

        The run's first and last lines are non-blank, so trimming always
        stops on a real character; only outer indentation and trailing
        padding are removed, while internal line breaks and inner spacing
        stay inside the span and count toward its length.

        Args:
            text: Full document text.
            start: Offset of the run's first line.
            end: Offset after the run's last character.
            lines: Number of lines in the run.

        Returns:
            Tuple[int, int, int, bool]: (start, end, chars, single_line).
        """
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        return start, end, end - start, lines == 1

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
            -> 'ParagraphStatsProfiler':
        """Initialize and validate the profiler from component configuration.

        Validation happens eagerly at load time: thresholds and ratios that
        would silently mislabel every document are far cheaper to catch as
        a startup failure than to discover in stored metadata later.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            ParagraphStatsProfiler: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "long_threshold") and \
                doc_processor_configer.long_threshold is not None:
            threshold = doc_processor_configer.long_threshold
            if isinstance(threshold, bool) or not isinstance(threshold, int):
                raise ValueError("long_threshold must be an integer")
            self.long_threshold = threshold
            if self.long_threshold < 1:
                raise ValueError("long_threshold must be >= 1")

        if hasattr(doc_processor_configer, "short_threshold") and \
                doc_processor_configer.short_threshold is not None:
            threshold = doc_processor_configer.short_threshold
            if isinstance(threshold, bool) or not isinstance(threshold, int):
                raise ValueError("short_threshold must be an integer")
            self.short_threshold = threshold
            if self.short_threshold < 0:
                raise ValueError("short_threshold must be >= 0")

        if hasattr(doc_processor_configer, "long_ratio") and \
                doc_processor_configer.long_ratio is not None:
            ratio = doc_processor_configer.long_ratio
            if isinstance(ratio, bool) or \
                    not isinstance(ratio, (int, float)):
                raise ValueError("long_ratio must be a number")
            self.long_ratio = float(ratio)
            if not 0 <= self.long_ratio <= 1:
                raise ValueError("long_ratio must be in [0, 1]")

        if hasattr(doc_processor_configer, "fragmented_ratio") and \
                doc_processor_configer.fragmented_ratio is not None:
            ratio = doc_processor_configer.fragmented_ratio
            if isinstance(ratio, bool) or \
                    not isinstance(ratio, (int, float)):
                raise ValueError("fragmented_ratio must be a number")
            self.fragmented_ratio = float(ratio)
            if not 0 <= self.fragmented_ratio <= 1:
                raise ValueError("fragmented_ratio must be in [0, 1]")

        if hasattr(doc_processor_configer, "stats_key") and \
                doc_processor_configer.stats_key is not None:
            key = doc_processor_configer.stats_key
            if not isinstance(key, str):
                raise ValueError("stats_key must be a string")
            self.stats_key = key

        if hasattr(doc_processor_configer, "flag_key") and \
                doc_processor_configer.flag_key is not None:
            key = doc_processor_configer.flag_key
            if not isinstance(key, str):
                raise ValueError("flag_key must be a string")
            self.flag_key = key

        if self.long_threshold < self.short_threshold:
            raise ValueError(
                "long_threshold must be >= short_threshold, got "
                f"{self.long_threshold} < {self.short_threshold}")

        return self
