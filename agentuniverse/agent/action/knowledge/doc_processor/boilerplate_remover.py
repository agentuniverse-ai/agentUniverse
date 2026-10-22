# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: boilerplate_remover.py

from collections import Counter
from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# A batch must contain at least this many documents before any line can be
# judged boilerplate: repetition needs cross-document evidence.
_MIN_BATCH_SIZE = 2

# Number of removed lines kept in metadata['boilerplate_sample'].
_SAMPLE_SIZE = 5


class BoilerplateRemover(DocProcessor):
    """Strip headers, footers and other boilerplate repeated across a batch.

    Documents that arrive together usually come from the same source, and
    that source stamps every page with text the reader never asked for:
    confidentiality banners, company footers, page numbers, navigation
    chrome, legal disclaimers. Left in place, these lines are chunked and
    embedded on every single document, wasting embedding budget and
    polluting chunk similarity — near-identical boilerplate chunks crowd
    the vector space and can surface as spurious recall hits. This
    processor runs *before* splitting/embedding and removes exactly that
    repeated material.

    Boilerplate is identified by cross-document frequency, the same idea
    behind classic crawler boilerplate detection, evaluated per batch:

    1. every line of every document is normalized — leading/trailing
       whitespace stripped, internal whitespace runs collapsed to single
       spaces — so "ACME Corp  Report" and " ACME Corp Report " count as
       the same line (case is deliberately NOT folded: "Confidential" and
       "CONFIDENTIAL" stay distinct);
    2. each normalized line is counted once per document it appears in
       (a header printed twice in one document counts once), over the
       number of documents in the batch;
    3. a line present in at least ``threshold`` fraction of the documents
       (default 0.6, boundary inclusive) OR in at least ``min_docs``
       documents (absolute count, disabled by default) becomes a
       boilerplate candidate;
    4. short lines are safe-listed: a normalized line shorter than
       ``min_line_len`` (default 4) is only removed when it appears in
       *every* document of the batch, which protects separators such as
       ``---``, ``***`` or stray bullets from threshold noise while still
       catching exact-everywhere repeats.

    By default (``mode='remove-lines'``) candidate lines are dropped from
    the text; the remaining lines are re-joined with newlines. A
    document's text is rewritten only when at least one of its lines was
    removed, so untouched documents keep their exact original string
    (line endings included); rewritten documents are joined with ``\n``.
    Blank lines are never candidates and never removed. With
    ``mode='tag-only'`` the text is left untouched and the detected lines
    are listed in ``metadata['boilerplate_lines']`` instead — useful for
    auditing a threshold change before trusting it.

    Every document that had at least one boilerplate line is stamped with
    ``metadata['boilerplate_removed_count']`` (how many of its lines were
    removed — or detected, in tag-only mode) and
    ``metadata['boilerplate_sample']`` (its first 5 such lines, in
    document order, in normalized form). Metadata mappings are copied
    before mutation, ids and document order are preserved, and no
    document is ever dropped — this is line-level cleanup, unlike
    ``SimHashDedupFilter`` / ``SemanticDeduplicator`` which remove whole
    near-duplicate documents.

    A batch of fewer than two documents passes through completely
    unchanged: repetition inside a single document is not evidence of
    boilerplate. The whole pipeline is pure Python, deterministic and
    offline — no model calls, no dependencies.

    Attributes:
        threshold: Fraction of the batch's documents a normalized line
            must appear in to count as boilerplate, in (0, 1]; the
            boundary is inclusive (3 of 5 documents satisfies 0.6).
        min_docs: Alternative absolute rule — a line present in at least
            this many documents is boilerplate regardless of ``threshold``.
            None (default) disables the rule; when set it must be >= 2,
            because a single-document match is never cross-document
            evidence.
        mode: ``remove-lines`` (default) drops boilerplate lines from the
            text; ``tag-only`` keeps the text untouched and records the
            findings in ``metadata['boilerplate_lines']``.
        min_line_len: Length (of the normalized line) below which a line
            is safe-listed — removed only when it appears in every
            document of the batch. Protects short structural lines such
            as ``---`` or ``*``. Must be >= 0; 0 disables the safe-list.
    """

    threshold: float = 0.6
    min_docs: Optional[int] = None
    mode: str = "remove-lines"
    min_line_len: int = 4

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Remove (or tag) lines repeated across the documents of a batch.

        Args:
            origin_docs: Documents to clean, in batch order.
            query: Query object (unused; boilerplate detection depends
                only on the documents' own text).

        Returns:
            List[Document]: The same document objects, in the same order,
            with cross-document boilerplate lines removed from the text
            (or tagged, in tag-only mode) and bookkeeping stamped into
            the metadata of affected documents.
        """
        if not origin_docs:
            return []

        # Repetition inside a single document is not evidence: batches
        # smaller than two documents pass through untouched.
        if len(origin_docs) < _MIN_BATCH_SIZE:
            return list(origin_docs)

        # Per-document original lines and their normalized forms. The
        # originals are kept for output so unique lines survive with
        # their exact spacing; only removed lines lose theirs.
        normalized_docs: List[List[str]] = []
        for doc in origin_docs:
            normalized_docs.append(
                [self._normalize(line) for line in (doc.text or "").splitlines()])

        # Count each normalized line once per document it appears in, so
        # a header printed twice within one document does not inflate its
        # own count.
        counts: Counter = Counter()
        for lines in normalized_docs:
            counts.update({line for line in lines if line})

        boilerplate = self._boilerplate_lines(counts, len(origin_docs))

        for doc, lines in zip(origin_docs, normalized_docs):
            removed = [line for line in lines if line in boilerplate]
            if not removed:
                continue
            if self.mode == "remove-lines":
                originals = (doc.text or "").splitlines()
                doc.text = "\n".join(
                    original for original, normalized in zip(originals, lines)
                    if normalized not in boilerplate)
            self._stamp(doc, "boilerplate_removed_count", len(removed))
            self._stamp(doc, "boilerplate_sample", removed[:_SAMPLE_SIZE])
            if self.mode == "tag-only":
                self._stamp(doc, "boilerplate_lines", removed)
        return origin_docs

    # ------------------------------------------------------------------ #
    # Detection helpers
    # ------------------------------------------------------------------ #

    def _boilerplate_lines(self, counts: Counter, doc_count: int) -> set:
        """Select which normalized lines count as boilerplate.

        Args:
            counts: Mapping of normalized line -> number of documents it
                appears in.
            doc_count: Total number of documents in the batch (the
                denominator of the threshold fraction).

        Returns:
            set: Normalized lines considered boilerplate.
        """
        boilerplate = set()
        for line, count in counts.items():
            if len(line) < self.min_line_len:
                # Short structural lines are safe-listed: only an exact
                # duplicate in every single document is removed. Such a
                # line trivially satisfies any threshold <= 1, so no
                # further check is needed.
                if count >= doc_count:
                    boilerplate.add(line)
                continue
            fraction = count / doc_count
            if fraction >= self.threshold or \
                    (self.min_docs is not None and count >= self.min_docs):
                boilerplate.add(line)
        return boilerplate

    @staticmethod
    def _normalize(line: str) -> str:
        """Normalize one line for cross-document comparison.

        Leading and trailing whitespace is stripped and internal
        whitespace runs are collapsed to single spaces, so differently
        indented or padded copies of the same header compare equal. Case
        is deliberately left alone: folding it would merge lines that
        only happen to share spelling.

        Args:
            line: Raw line from a document.

        Returns:
            str: The whitespace-normalized line.
        """
        return " ".join(line.split())

    @staticmethod
    def _stamp(doc: Document, key: str, value) -> None:
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
            -> 'BoilerplateRemover':
        """Initialize and validate the remover from component configuration.

        Validation happens eagerly at load time: a silently misconfigured
        remover that deleted the wrong lines would be far harder to notice
        in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            BoilerplateRemover: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "threshold") and \
                doc_processor_configer.threshold is not None:
            threshold = doc_processor_configer.threshold
            if isinstance(threshold, bool) or \
                    not isinstance(threshold, (int, float)):
                raise ValueError("threshold must be a number")
            self.threshold = float(threshold)
            if not 0 < self.threshold <= 1:
                raise ValueError("threshold must be in (0, 1]")

        if hasattr(doc_processor_configer, "min_docs") and \
                doc_processor_configer.min_docs is not None:
            min_docs = doc_processor_configer.min_docs
            if isinstance(min_docs, bool) or not isinstance(min_docs, int):
                raise ValueError("min_docs must be an integer")
            self.min_docs = min_docs
            if self.min_docs < _MIN_BATCH_SIZE:
                raise ValueError(
                    f"min_docs must be >= {_MIN_BATCH_SIZE}, got "
                    f"{self.min_docs}")

        if hasattr(doc_processor_configer, "mode") and \
                doc_processor_configer.mode is not None:
            self.mode = doc_processor_configer.mode
            if self.mode not in ("remove-lines", "tag-only"):
                raise ValueError(
                    "mode must be 'remove-lines' or 'tag-only', got "
                    f"'{self.mode}'")

        if hasattr(doc_processor_configer, "min_line_len") and \
                doc_processor_configer.min_line_len is not None:
            min_line_len = doc_processor_configer.min_line_len
            if isinstance(min_line_len, bool) or \
                    not isinstance(min_line_len, int):
                raise ValueError("min_line_len must be an integer")
            self.min_line_len = min_line_len
            if self.min_line_len < 0:
                raise ValueError("min_line_len must be >= 0")

        return self
