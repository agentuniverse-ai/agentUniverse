# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/06
# @FileName: temporal_decay_filter.py

import math
from datetime import datetime, timezone
from typing import Any, List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger

# Number of seconds in one day; ages are computed in day units so that the
# half-life can be expressed directly in days.
_SECONDS_PER_DAY = 86400.0

# Epoch-millisecond detection threshold: any numeric timestamp at or above
# this magnitude is interpreted as milliseconds since the Unix epoch rather
# than seconds. 1e11 seconds would be the year 5138 — far beyond any real
# seconds-based pipeline — while 1e11 milliseconds is early 1973, below every
# realistically indexed document.
_EPOCH_MILLIS_THRESHOLD = 1e11


class TemporalDecayFilter(DocProcessor):
    """Filter recalled documents by exponential temporal decay.

    Many knowledge bases mix fresh and stale documents: a news corpus holds
    today's wire stories next to decade-old analyses, and a wiki-based store
    keeps superseded revisions. When such a corpus is recalled for a query,
    equally relevant hits of very different ages are not equally useful. This
    processor scores every document with a classic exponential half-life decay

        score = exp(-ln(2) * age_days / half_life_days)

    so a document exactly ``half_life_days`` old scores 0.5, twice the
    half-life scores 0.25, and so on. Documents scoring below ``min_score``
    (or older than the hard cap ``max_age_days``) are dropped; surviving
    documents carry the score in ``metadata[decay_score_key]`` so downstream
    rerankers / fusion processors can combine freshness with relevance.

    Timestamps are read from ``metadata[timestamp_key]`` and accepted in the
    common shapes produced by real pipelines: epoch seconds, epoch
    milliseconds, ISO 8601 strings (with or without ``Z`` / offset), and
    ``datetime`` objects. Documents whose timestamp is missing or unparsable
    are kept or dropped according to ``missing_timestamp``.

    Attributes:
        timestamp_key: Metadata field holding each document's timestamp.
        max_age_days: Optional hard age cap; older documents are always
            dropped regardless of the decay score. ``None`` disables the cap.
        half_life_days: Age in days at which the decay score equals 0.5.
            Must be positive.
        min_score: Decay score below which a document is dropped, in (0, 1].
        decay_score_key: Metadata key the score is written to; an empty value
            disables score stamping.
        missing_timestamp: ``keep`` or ``drop`` — what happens to documents
            without a usable timestamp.
        reference_time: Optional evaluation instant as epoch seconds. Fixed
            at load time so scoring is deterministic for testing and
            replayable pipelines; defaults to the moment of initialization.
    """

    timestamp_key: str = "timestamp"
    max_age_days: Optional[float] = None
    half_life_days: float = 30.0
    min_score: float = 0.1
    decay_score_key: str = "decay_score"
    missing_timestamp: str = "keep"
    reference_time: Optional[float] = None

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Score documents by temporal decay and drop the stale ones.

        Args:
            origin_docs: Recalled documents to filter.
            query: Query object (unused; decay depends only on time).

        Returns:
            List[Document]: Documents that survive the decay / age criteria,
            in their original order, each stamped with its decay score.
        """
        if not origin_docs:
            return []

        reference = self._reference_now()
        kept: List[Document] = []
        for doc in origin_docs:
            timestamp = self._extract_timestamp(doc)
            if timestamp is None:
                if self.missing_timestamp == "drop":
                    continue
                kept.append(doc)
                continue

            age_days = (reference - timestamp) / _SECONDS_PER_DAY
            score = self._decay_score(age_days)

            # The hard age cap wins over the decay curve: it guarantees an
            # absolute staleness boundary that a slowly-decaying half-life
            # alone would let through.
            if self.max_age_days is not None and age_days > self.max_age_days:
                continue
            if score < self.min_score:
                continue

            self._stamp_score(doc, score)
            kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Scoring helpers
    # ------------------------------------------------------------------ #

    def _decay_score(self, age_days: float) -> float:
        """Return the decay score for an age expressed in days.

        Future-dated timestamps (negative age) are clamped to a full score of
        1.0 — clock skew between indexing and query time must not amplify a
        document above unity or punish it for arriving "from the future".

        Args:
            age_days: Document age in days (may be negative).

        Returns:
            float: Score in (0.0, 1.0]; 1.0 for age <= 0.
        """
        if age_days <= 0:
            return 1.0
        return math.exp(-math.log(2) * age_days / self.half_life_days)

    def _stamp_score(self, doc: Document, score: float) -> None:
        """Write the decay score into the document metadata.

        The metadata mapping is copied before mutation so a document shared
        with other pipeline stages never observes surprising in-place edits.

        Args:
            doc: Document to stamp.
            score: Computed decay score.
        """
        if not self.decay_score_key:
            return
        meta = dict(doc.metadata or {})
        meta[self.decay_score_key] = round(score, 6)
        doc.metadata = meta

    def _reference_now(self) -> float:
        """Return the evaluation instant as epoch seconds.

        Uses the pinned ``reference_time`` when one was configured, else the
        current wall-clock time.

        Returns:
            float: Epoch seconds used as "now" for every age computation.
        """
        if self.reference_time is not None:
            return float(self.reference_time)
        return datetime.now(timezone.utc).timestamp()

    # ------------------------------------------------------------------ #
    # Timestamp extraction
    # ------------------------------------------------------------------ #

    def _extract_timestamp(self, doc: Document) -> Optional[float]:
        """Extract an epoch-seconds timestamp from document metadata.

        Supported value shapes under ``metadata[timestamp_key]``:

        * ``int`` / ``float`` — epoch seconds, or epoch milliseconds when the
          magnitude clearly exceeds the seconds range;
        * ``str`` — numeric epoch (seconds or milliseconds) or ISO 8601 with
          optional ``Z`` suffix / date-only form;
        * ``datetime.datetime`` — naive values are assumed UTC.

        Args:
            doc: Document whose metadata is inspected.

        Returns:
            Optional[float]: Epoch seconds, or None when absent/unparsable.
        """
        if not doc.metadata:
            return None
        value = doc.metadata.get(self.timestamp_key)
        if value is None:
            return None
        try:
            return self._coerce_timestamp(value)
        except (TypeError, ValueError, OverflowError):
            return None

    @staticmethod
    def _coerce_timestamp(value: Any) -> float:
        """Coerce one metadata value to epoch seconds.

        Args:
            value: Raw timestamp value in any supported shape.

        Returns:
            float: Epoch seconds.

        Raises:
            TypeError: For types that can never denote a timestamp.
            ValueError: For strings that are neither numeric nor ISO 8601.
        """
        if isinstance(value, bool):
            # bool is an int subclass; a boolean is never a timestamp.
            raise TypeError("boolean is not a timestamp")
        if isinstance(value, (int, float)):
            seconds = float(value)
            if abs(seconds) >= _EPOCH_MILLIS_THRESHOLD:
                seconds /= 1000.0
            return seconds
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc).timestamp()
            return value.timestamp()
        if isinstance(value, str):
            text = value.strip()
            try:
                return TemporalDecayFilter._coerce_timestamp(float(text))
            except ValueError:
                return TemporalDecayFilter._parse_iso8601(text)
        raise TypeError(f"unsupported timestamp type: {type(value).__name__}")

    @staticmethod
    def _parse_iso8601(text: str) -> float:
        """Parse an ISO 8601 string to epoch seconds.

        Handles the trailing ``Z`` still emitted by many producers (Python's
        ``fromisoformat`` only learned it in 3.11) and treats naive timestamps
        as UTC, matching the epoch-seconds convention used elsewhere here.

        Args:
            text: ISO 8601 string, date-only allowed.

        Returns:
            float: Epoch seconds.

        Raises:
            ValueError: When the string is not valid ISO 8601.
        """
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #

    def _initialize_by_component_configer(
            self, doc_processor_configer: ComponentConfiger) \
            -> 'TemporalDecayFilter':
        """Initialize and validate the filter from component configuration.

        Validation happens eagerly at load time: a misconfigured decay filter
        that silently passed every document through would be far harder to
        notice in production than a startup failure.

        Args:
            doc_processor_configer: Configuration object.

        Returns:
            TemporalDecayFilter: The initialized instance.

        Raises:
            ValueError: On an invalid combination of parameter values.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "timestamp_key"):
            self.timestamp_key = doc_processor_configer.timestamp_key
            if not self.timestamp_key:
                raise ValueError("timestamp_key must be a non-empty string")

        if hasattr(doc_processor_configer, "max_age_days") and \
                doc_processor_configer.max_age_days is not None:
            self.max_age_days = doc_processor_configer.max_age_days
            if self.max_age_days <= 0:
                raise ValueError("max_age_days must be positive when set")

        if hasattr(doc_processor_configer, "half_life_days"):
            self.half_life_days = doc_processor_configer.half_life_days
            if self.half_life_days <= 0:
                raise ValueError("half_life_days must be positive")

        if hasattr(doc_processor_configer, "min_score"):
            self.min_score = doc_processor_configer.min_score
            if not 0 < self.min_score <= 1:
                raise ValueError("min_score must be in (0, 1]")

        if hasattr(doc_processor_configer, "decay_score_key"):
            self.decay_score_key = doc_processor_configer.decay_score_key

        if hasattr(doc_processor_configer, "missing_timestamp"):
            self.missing_timestamp = doc_processor_configer.missing_timestamp
            if self.missing_timestamp not in ("keep", "drop"):
                raise ValueError(
                    "missing_timestamp must be 'keep' or 'drop', got "
                    f"'{self.missing_timestamp}'")

        if hasattr(doc_processor_configer, "reference_time") and \
                doc_processor_configer.reference_time is not None:
            self.reference_time = doc_processor_configer.reference_time

        return self
