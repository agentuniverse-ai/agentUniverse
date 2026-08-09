# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: length_filter.py

"""
Length-filter document pre-processor.

Filters the documents recalled by a RAG pipeline by their **length**, so
documents that are too short to be informative (fragments, boilerplate,
single-word hits) or too long to be useful (dumped whole pages) can be
dropped *before* they reach the LLM.

It is a focused, per-document predicate processor — the *length-only*
direction of issue #258. It is distinct from:

* ``ThresholdFilter`` — a general filter combinator that supports score /
  length / top-k / percentile filters with AND/OR logic. ``LengthFilter``
  is a single-purpose, configuration-light component for users who only
  need length filtering, with an explicit length-unit selector
  (``counter``) and an explicit ``drop_mode``.
* ``ContextBudgetCompressor`` — manages the **cumulative** size of the
  kept set and can split the boundary document. ``LengthFilter`` only
  applies a per-document length range and never truncates.

Length is measured explicitly and honestly via ``counter``:

* ``"char"`` — exact character count (default).
* ``"word"`` — exact whitespace word count.
* ``"token"`` — BPE token count via ``tiktoken`` (encoding configurable);
  falls back to the chars/4 estimate with a warning if tiktoken is not
  installed.

``drop_mode`` controls which side of the range is removed:

* ``"drop_short"`` — remove documents whose length is below ``min_length``.
* ``"drop_long"``  — remove documents whose length is above ``max_length``.
* ``"both"``       — remove documents outside ``[min_length, max_length]``.
"""

import logging
from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

_VALID_COUNTERS = {"char", "word", "token"}
_VALID_DROP_MODES = {"drop_short", "drop_long", "both"}

# Cache of tiktoken encoders keyed by encoding name. Keying by name means
# multiple filter instances can use different encodings, and a failed lookup
# for one encoding never poisons another. A value of None means "tiktoken not
# installed" for that name.
_TIKTOKEN_ENCODERS: dict = {}


class LengthFilter(DocProcessor):
    """Filter documents by their text length.

    Attributes:
        min_length: Minimum inclusive length; documents shorter than this are
            dropped when ``drop_mode`` includes the short side. ``0`` disables
            the lower bound.
        max_length: Maximum inclusive length; documents longer than this are
            dropped when ``drop_mode`` includes the long side. ``0`` (the
            default) disables the upper bound.
        counter: How each document's length is measured: ``"char"`` (default),
            ``"word"``, or ``"token"`` (BPE tokens via tiktoken).
        drop_mode: Which side of the range is removed: ``"drop_short"``,
            ``"drop_long"``, or ``"both"``.
        tiktoken_encoding: Encoding passed to ``tiktoken`` when
            ``counter == "token"``.
    """

    min_length: int = 0
    max_length: int = 0
    counter: str = "char"
    drop_mode: str = "drop_short"
    tiktoken_encoding: str = "cl100k_base"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Filter documents by their length according to ``drop_mode``.

        Args:
            origin_docs: Documents to be filtered.
            query: Unused; kept for interface compatibility.

        Returns:
            Documents whose length satisfies the configured bounds and drop
            mode. Original order is preserved.
        """
        if not origin_docs:
            return []

        kept: List[Document] = []
        for doc in origin_docs:
            length = self._count(doc.text or "")
            if self._keep(length):
                kept.append(doc)
        return kept

    # ------------------------------------------------------------------ #
    # Length measurement & decision
    # ------------------------------------------------------------------ #

    def _keep(self, length: int) -> bool:
        """Decide whether a document of the given length is kept.

        Args:
            length: The document length in the unit of ``counter``.

        Returns:
            True if the document passes the filter, False otherwise.
        """
        drop_short = self.drop_mode in ("drop_short", "both")
        drop_long = self.drop_mode in ("drop_long", "both")

        if drop_short and self.min_length > 0 and length < self.min_length:
            return False
        if drop_long and self.max_length > 0 and length > self.max_length:
            return False
        return True

    def _count(self, text: str) -> int:
        """Measure the length of ``text`` in the unit of ``counter``.

        Args:
            text: The raw document text.

        Returns:
            The length as a non-negative integer.
        """
        if self.counter == "char":
            return len(text)
        if self.counter == "word":
            return len(text.split())
        if self.counter == "token":
            encoder = _tiktoken_encoder(self.tiktoken_encoding)
            if encoder is not None:
                return len(encoder.encode(text))
            logger.warning(
                "tiktoken is not available; counting with the chars/4 estimate "
                "instead. Install tiktoken or set counter to 'char'/'word' to "
                "silence this.")
        # Fallback when counter is unknown or tiktoken is unavailable.
        return max(1, len(text) // 4) if text else 0

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'LengthFilter':
        """Initialize the filter from its component config.

        Validates ``counter`` and ``drop_mode`` eagerly so a bad config fails
        at component initialization rather than silently disabling filtering.

        Args:
            doc_processor_configer: Configuration object for the doc processor.

        Returns:
            The initialized filter instance.

        Raises:
            ValueError: If ``counter`` or ``drop_mode`` is invalid.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "min_length"):
            self.min_length = doc_processor_configer.min_length
        if hasattr(doc_processor_configer, "max_length"):
            self.max_length = doc_processor_configer.max_length
        if hasattr(doc_processor_configer, "counter"):
            self.counter = doc_processor_configer.counter
        if hasattr(doc_processor_configer, "drop_mode"):
            self.drop_mode = doc_processor_configer.drop_mode
        if hasattr(doc_processor_configer, "tiktoken_encoding"):
            self.tiktoken_encoding = doc_processor_configer.tiktoken_encoding

        if self.counter not in _VALID_COUNTERS:
            raise ValueError(
                f"counter must be one of {sorted(_VALID_COUNTERS)}, "
                f"got '{self.counter}'.")
        if self.drop_mode not in _VALID_DROP_MODES:
            raise ValueError(
                f"drop_mode must be one of {sorted(_VALID_DROP_MODES)}, "
                f"got '{self.drop_mode}'.")
        return self


def _tiktoken_encoder(encoding: str):
    """Return a cached tiktoken encoder for ``encoding``.

    Two distinct failure modes are handled differently:

    * tiktoken is not installed (an optional dependency) -> return None so the
      caller degrades to the estimate counter with a warning. This is a
      legitimate graceful fallback for a missing dependency.
    * tiktoken is installed but ``encoding`` is not a known encoding name ->
      raise ValueError. A bad configuration must fail loudly rather than
      silently switching the counting unit from tokens to the chars/4 estimate.

    Results are cached per encoding name, so one instance's encoder is never
    handed to another instance that configured a different encoding, and an
    invalid name does not poison subsequent lookups.
    """
    if encoding in _TIKTOKEN_ENCODERS:
        return _TIKTOKEN_ENCODERS[encoding]

    try:
        import tiktoken
    except ImportError as exc:
        logger.debug("tiktoken is not installed; degrading to the estimate counter: %s", exc)
        _TIKTOKEN_ENCODERS[encoding] = None
        return None

    try:
        encoder = tiktoken.get_encoding(encoding)
    except Exception as exc:
        raise ValueError(f"Invalid tiktoken encoding {encoding!r}: {exc}") from exc

    _TIKTOKEN_ENCODERS[encoding] = encoder
    return encoder
