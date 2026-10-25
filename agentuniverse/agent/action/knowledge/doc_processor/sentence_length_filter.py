# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: sentence_length_filter.py

import math
from typing import List, Tuple

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Characters that terminate a sentence: Latin and CJK full stops,
# exclamation marks and question marks.
_TERMINAL_CHARS = ".!?。！？"

# Closing quotes / brackets swallowed into the finished sentence right
# after its terminal punctuation, so spans like '"Are you sure?"' stay whole.
_CLOSING_CHARS = "\"'”’」』》）】)]"

# English words that, when the only thing following them is a dot, do NOT
# end a sentence ("Dr. Smith asked..."). Lowercase; matched on the alpha run
# immediately before the dot. Single-letter initials ("J.", "e.g.") are
# handled separately by length, which is why they are absent here.
_ABBREVIATIONS = frozenset((
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "mt", "rev", "hon",
    "gen", "col", "capt", "lt", "sgt", "vs", "etc", "inc", "ltd", "co",
    "corp", "dept", "univ", "assn", "bros", "no", "nos", "vol", "vols",
    "fig", "figs", "eq", "approx", "est", "cf", "al", "ca", "ed", "eds",
    "pp", "ch", "sec", "para", "ph", "md", "ba", "ma", "msc", "jan", "feb",
    "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
))

# Metadata keys: the outlier list, and (drop / keep_only modes only) the
# bookkeeping of what the mode removed from the text.
_OUTLIERS_KEY = "sentence_outliers"
_REMOVED_COUNT_KEY = "sentence_removed_count"
_REMOVED_KEY = "sentence_removed"

# Maximum number of removed sentence texts kept in metadata; the count
# metadata is always the uncapped total, so a capped list never hides the
# true magnitude.
_REMOVED_TEXTS_CAP = 10

_MODES = ("tag", "drop", "keep_only")


class SentenceLengthFilter(DocProcessor):
    """Tag or drop statistical sentence-length outliers inside prose.

    Real knowledge documents are prose with parasites: a boilerplate run
    repeated under every product description, a legal disclaimer pasted
    at the end of each page, a table dumped mid-paragraph as one
    comma-separated line. Those outlier sentences carry no topical signal,
    yet they ride along into every chunk, dilute the embedding of the
    surrounding prose and skew retrieval toward boilerplate. This
    pre-processing component segments each document into sentences
    (conservative segmentation in the same family as ``QuestionDetector``:
    ``. ! ?`` plus ``。！？`` boundaries, with abbreviation / initial /
    decimal / ellipsis guards on the Latin dot), measures every sentence
    in characters, and flags statistical outliers — sentences far longer
    than the document's own norm — plus anything over an absolute cap.

    A sentence is an outlier when its character length (terminal
    punctuation and closing quotes included) is **strictly greater** than
    ``mean + k * stdev`` or **strictly greater** than ``max_chars``; a
    sentence exactly at either threshold is kept. The mean and the
    population standard deviation (divide-by-n) are computed over the
    document's own sentences, so the norm adapts to the register of each
    document — a patent's "long" is a tweet's "impossible". The
    statistical rule needs a meaningful sample: with fewer than
    ``min_sentences`` (default 3) sentences only the absolute cap applies,
    because a mean over two sentences is noise, not a norm. The absolute
    cap always applies, in either regime, as a backstop for short
    documents and for docs where every sentence is inflated.

    Three modes consume the outliers:

    * ``tag`` (default) — text is left untouched and every outlier is
      stamped into ``metadata['sentence_outliers']`` as
      ``{"index": i, "length": L, "span": (start, end)}``, where ``index``
      is the sentence's position among the document's sentences and
      ``span`` are character offsets into the text with
      ``text[start:end]`` equal to the sentence. Downstream stages decide
      what to do; spans are ordered and non-overlapping.
    * ``drop`` — outlier sentences are removed from the text and the
      survivors rejoined with single spaces; ``metadata``
      ``['sentence_removed_count']`` records the uncapped number of
      removed sentences and ``metadata['sentence_removed']`` their texts
      capped at 10 (the count is never capped). When nothing is removed
      the text is returned byte-identical — no rejoin, no whitespace
      normalisation — so the filter is safe to leave in a pipeline.
    * ``keep_only`` — the inverse: only the outlier sentences survive,
      rejoined with single spaces, and the bookkeeping records the normal
      sentences that were removed. This is the boilerplate-inspection
      mode: run it over a corpus and read the output to see exactly which
      boilerplate runs, disclaimers and table dumps pollute it, before
      deciding thresholds for a ``drop`` pass.

    In every mode the outlier list refers to the text as it was before
    this processor ran. Existing metadata entries are preserved, metadata
    mappings are copied before mutation, and id / other fields are never
    touched. The whole pipeline is pure Python, deterministic and
    offline — no models, no network, no dependencies.

    The component is deliberately narrow and therefore complementary to
    its neighbours: ``ThresholdFilter`` bounds whole-document sizes (this
    one works *inside* a document, at sentence granularity),
    ``ParagraphStatsProfiler`` measures paragraph structure,
    ``QuestionDetector`` and ``SentencePositionTagger`` classify
    sentences rather than measuring them, and splitting components run
    after outliers are gone so chunks are not born polluted.

    Attributes:
        k: Multiplier of the standard deviation in the statistical
            outlier rule; must be > 0. Default 2.0 — roughly the classic
            95% band for near-normal sentence-length distributions.
        max_chars: Absolute cap on sentence character length; must be
            >= 1. A sentence strictly longer is an outlier regardless of
            statistics. Default 500.
        min_sentences: Minimum number of sentences for the statistical
            rule to apply; must be >= 1. Below it only ``max_chars``
            applies. Default 3.
        mode: What to do with outliers — ``tag`` (default), ``drop`` or
            ``keep_only``.
    """

    k: float = 2.0
    max_chars: int = 500
    min_sentences: int = 3
    mode: str = "tag"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Tag or drop sentence-length outliers in every document.

        Args:
            origin_docs: Documents to process, in batch order.
            query: Query object (unused; outlier detection depends only
                on the documents' own text).

        Returns:
            List[Document]: The same documents, in the same order, with
            outlier bookkeeping in metadata and — in ``drop`` /
            ``keep_only`` modes — outlier sentences removed from or
            reduced to in the text.
        """
        if not origin_docs:
            return []

        for doc in origin_docs:
            self._process_one(doc)
        return origin_docs

    def _process_one(self, doc: Document) -> None:
        """Apply the configured mode to one document.

        Args:
            doc: Document to process; text and metadata are updated in
                place according to ``mode``.
        """
        text = doc.text or ""
        spans = self._sentences(text)
        lengths = [end - start for start, end in spans]
        outliers = set(self._outlier_indices(lengths))

        entries = [{"index": i, "length": lengths[i], "span": spans[i]}
                   for i in sorted(outliers)]
        self._stamp(doc, _OUTLIERS_KEY, entries)

        if self.mode == "tag":
            return

        # drop keeps the normal sentences; keep_only keeps the outliers.
        if self.mode == "drop":
            survivors = [i for i in range(len(spans))
                         if i not in outliers]
        else:  # keep_only
            survivors = sorted(outliers)
        removed = [i for i in range(len(spans)) if i not in set(survivors)]

        if removed:
            # Rebuild from the surviving sentences, joined with single
            # spaces; inter-sentence whitespace and punctuation-only
            # husks do not survive a rebuild. When nothing is removed
            # the text stays byte-identical instead.
            doc.text = " ".join(text[spans[i][0]:spans[i][1]]
                                for i in survivors)
        self._stamp(doc, _REMOVED_COUNT_KEY, len(removed))
        self._stamp(doc, _REMOVED_KEY,
                    [text[spans[i][0]:spans[i][1]]
                     for i in removed][:_REMOVED_TEXTS_CAP])

    # ------------------------------------------------------------------ #
    # Statistics
    # ------------------------------------------------------------------ #

    def _outlier_indices(self, lengths: List[int]) -> List[int]:
        """Return the sorted indices of outlier sentence lengths.

        Absolute cap first (always active), then the statistical rule
        when the document has at least ``min_sentences`` sentences. Both
        comparisons are strictly greater: a length exactly at
        ``max_chars`` or exactly at ``mean + k * stdev`` is not an
        outlier.

        Args:
            lengths: Character lengths of the document's sentences.

        Returns:
            List[int]: Sorted, de-duplicated indices into ``lengths``.
        """
        outliers = {i for i, length in enumerate(lengths)
                    if length > self.max_chars}

        n = len(lengths)
        if n >= self.min_sentences:
            mean = sum(lengths) / n
            variance = sum((length - mean) ** 2 for length in lengths) / n
            stdev = math.sqrt(variance)
            threshold = mean + self.k * stdev
            outliers.update(i for i, length in enumerate(lengths)
                            if length > threshold)
        return sorted(outliers)

    # ------------------------------------------------------------------ #
    # Segmentation (conservative, same family as QuestionDetector)
    # ------------------------------------------------------------------ #

    def _sentences(self, text: str) -> List[Tuple[int, int]]:
        """Split text into sentence spans.

        A sentence is a maximal run of non-terminal characters plus its
        terminating punctuation run and closing quotes. Boundaries are
        ``. ! ?`` and ``。！？``; the dot additionally respects the
        abbreviation, single-letter-initial, decimal and ellipsis guards,
        so "Dr. Smith asked. Ms. Lee replied." yields exactly two
        sentences. Leading whitespace is skipped, so every span satisfies
        ``text[start:end]`` exactly. A segment must contain at least one
        alphanumeric character (CJK included) to count as a sentence —
        bare punctuation husks are not measured, not flagged and not
        preserved by rebuilds.

        Args:
            text: Raw document text.

        Returns:
            List[Tuple[int, int]]: Ordered, non-overlapping (start, end)
            character offsets of word-bearing sentences.
        """
        spans: List[Tuple[int, int]] = []
        length = len(text)
        start = 0
        i = 0
        while i < length:
            if text[i] in _TERMINAL_CHARS and self._is_boundary(text, i):
                end = i + 1
                # A run of terminal punctuation ("？！", "!!") plus any
                # closing quotes belongs to the sentence it terminates.
                while end < length and text[end] in _TERMINAL_CHARS:
                    end += 1
                while end < length and text[end] in _CLOSING_CHARS:
                    end += 1
                if self._has_word(text[start:end]):
                    spans.append((start, end))
                start = end
                while start < length and text[start].isspace():
                    start += 1
                i = start
            else:
                i += 1
        # Trailing sentence without terminal punctuation ("...and then").
        if start < length and self._has_word(text[start:length]):
            spans.append((start, length))
        return spans

    @staticmethod
    def _is_boundary(text: str, index: int) -> bool:
        """Report whether the terminal character at index really splits.

        Args:
            text: Full document text.
            index: Position of the candidate terminal character.

        Returns:
            bool: True when a sentence boundary, False for dots inside
            ellipses, decimals, abbreviations and initials. Non-dot
            terminals (! ? 。！？) always split.
        """
        if text[index] != ".":
            return True
        # Ellipsis "..." splits only at its final dot.
        if index + 1 < len(text) and text[index + 1] == ".":
            return False
        # Decimal point inside a number.
        if index > 0 and text[index - 1].isdigit() and \
                index + 1 < len(text) and text[index + 1].isdigit():
            return False
        # Alpha run immediately before the dot.
        j = index
        while j > 0 and text[j - 1].isalpha():
            j -= 1
        word = text[j:index]
        # Single-letter initial: "J.", "e.g.", "a.m.".
        if len(word) == 1:
            return False
        return word.lower() not in _ABBREVIATIONS

    @staticmethod
    def _has_word(sentence: str) -> bool:
        """Report whether a segment carries at least one word.

        A word is any alphanumeric character (CJK ideographs included),
        so "为什么？" carries one and a bare "？" carries none.

        Args:
            sentence: Segment text.

        Returns:
            bool: True when the segment counts as a sentence.
        """
        return any(ch.isalnum() for ch in sentence)

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
            -> 'SentenceLengthFilter':
        """Initialize and validate the filter from component configuration.

        Validation happens eagerly at load time: a misconfigured filter
        that silently tagged nothing (or dropped everything) would be far
        harder to notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            SentenceLengthFilter: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "k") and \
                doc_processor_configer.k is not None:
            value = doc_processor_configer.k
            if isinstance(value, bool) or \
                    not isinstance(value, (int, float)):
                raise ValueError("k must be a number")
            self.k = value
            if self.k <= 0:
                raise ValueError("k must be > 0")

        if hasattr(doc_processor_configer, "max_chars") and \
                doc_processor_configer.max_chars is not None:
            value = doc_processor_configer.max_chars
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("max_chars must be an integer")
            self.max_chars = value
            if self.max_chars < 1:
                raise ValueError("max_chars must be >= 1")

        if hasattr(doc_processor_configer, "min_sentences") and \
                doc_processor_configer.min_sentences is not None:
            value = doc_processor_configer.min_sentences
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("min_sentences must be an integer")
            self.min_sentences = value
            if self.min_sentences < 1:
                raise ValueError("min_sentences must be >= 1")

        if hasattr(doc_processor_configer, "mode") and \
                doc_processor_configer.mode is not None:
            self.mode = doc_processor_configer.mode
            if self.mode not in _MODES:
                raise ValueError(
                    "mode must be one of " + ", ".join(_MODES) +
                    f", got '{self.mode}'")

        return self
