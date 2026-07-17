# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/16
# @FileName: context_budget_compressor.py

"""
Context-budget compressor post-processor.

Fits the documents recalled by a RAG pipeline into a fixed budget (typically
the LLM's context window). It walks the recalled list — already ranked by the
store / an earlier reranker or fusion processor — and keeps documents in order
while their cumulative size stays within ``budget``; the boundary document that
would overflow is optionally truncated so the result uses the budget as fully as
possible without exceeding it.

This is the *post-processing* direction of issue #248 (knowledge post-
processing components). It operates on a different axis from
``ThresholdFilter``: ``ThresholdFilter`` applies per-document predicates (a
score / length range) or a fixed top-k, whereas this component manages the
**cumulative** size of the kept set and can split the last document to fit —
i.e. "how much context can I afford", not "does this one doc pass".

Counting is explicit and honestly named via ``counter``:

* ``"estimate"`` (default) — ``max(1, len(text) // 4)``, a fast, dependency-free
  approximation of tokens suitable for budgeting.
* ``"tiktoken"`` — real BPE token count via ``tiktoken`` (encoding configurable)
  when that package is installed; falls back to the estimate with a warning if
  it is not.
* ``"char"`` — exact character count.
* ``"word"`` — exact whitespace word count.

The budget is interpreted in the unit of the chosen counter, so the contract is
never "tokens" while silently counting words.
"""

import logging
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

_VALID_COUNTERS = {"estimate", "tiktoken", "char", "word"}

# Cache of tiktoken encoders keyed by encoding name. Keying by name (rather
# than a single module-global slot) means multiple compressor instances can use
# different encodings, and a failed lookup for one encoding never poisons
# another. A value of None means "tiktoken not installed" for that name.
_TIKTOKEN_ENCODERS: Dict[str, Optional[object]] = {}


class ContextBudgetCompressor(DocProcessor):
    """Trim the recalled set to a cumulative size budget.

    Attributes:
        budget: Maximum cumulative size of the kept documents, in the unit of
            ``counter``.
        counter: How each document's size is measured: ``"estimate"``
            (chars/4, default), ``"tiktoken"`` (BPE tokens), ``"char"``, or
            ``"word"``.
        truncate: When True, the first document that would exceed the budget is
            shortened so its size equals the remaining budget and included as
            the last result; when False, processing stops at that document.
        tiktoken_encoding: Encoding passed to ``tiktoken`` when
            ``counter == "tiktoken"``.
    """

    budget: int = 4096
    counter: str = "estimate"
    truncate: bool = True
    tiktoken_encoding: str = "cl100k_base"

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Keep documents in order until their cumulative size reaches budget.

        Args:
            origin_docs: Documents recalled by the knowledge query, assumed to
                be in relevance order (place this processor after a reranker or
                fusion processor when that is not the case).
            query: Unused; kept for interface compatibility.

        Returns:
            Documents fitting within ``budget``; the last one may be truncated
            when ``truncate`` is set.
        """
        if not origin_docs or self.budget <= 0:
            return []

        kept: List[Document] = []
        used = 0
        for doc in origin_docs:
            size = self._count(doc.text or "")
            if used + size <= self.budget:
                kept.append(doc)
                used += size
                continue
            if not self.truncate:
                break
            remaining = self.budget - used
            truncated_text = self._truncate(doc.text or "", remaining)
            if truncated_text:
                metadata = dict(doc.metadata or {})
                metadata["truncated"] = True
                kept.append(Document(text=truncated_text, metadata=metadata,
                                     id=doc.id))
            break  # budget exhausted after the (possibly truncated) boundary doc
        return kept

    # ------------------------------------------------------------------ #
    # Counting / truncation
    # ------------------------------------------------------------------ #
    def _count(self, text: str) -> int:
        if self.counter == "char":
            return len(text)
        if self.counter == "word":
            return len(text.split())
        if self.counter == "tiktoken":
            encoder = _tiktoken_encoder(self.tiktoken_encoding)
            if encoder is not None:
                return len(encoder.encode(text))
            logger.warning(
                "tiktoken is not available; counting with the chars/4 estimate "
                "instead. Install tiktoken or set counter to 'estimate'/'char'/"
                "'word' to silence this.")
        # "estimate" (also the tiktoken-unavailable fallback).
        return max(1, len(text) // 4)

    def _truncate(self, text: str, remaining: int) -> str:
        """Return a prefix of ``text`` whose size is at most ``remaining``."""
        if remaining <= 0:
            return ""
        if self.counter == "char":
            return text[:remaining]
        if self.counter == "word":
            return " ".join(text.split()[:remaining])
        if self.counter == "tiktoken":
            encoder = _tiktoken_encoder(self.tiktoken_encoding)
            if encoder is not None:
                return encoder.decode(encoder.encode(text)[:remaining])
        # "estimate" (and the tiktoken-unavailable fallback): ~4 chars per unit.
        return text[:remaining * 4]

    def _initialize_by_component_configer(self,
                                          doc_processor_configer: ComponentConfiger) \
            -> 'ContextBudgetCompressor':
        """Initialize the compressor from its component config."""
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "budget"):
            self.budget = doc_processor_configer.budget
        if hasattr(doc_processor_configer, "counter"):
            self.counter = doc_processor_configer.counter
        if hasattr(doc_processor_configer, "truncate"):
            self.truncate = doc_processor_configer.truncate
        if hasattr(doc_processor_configer, "tiktoken_encoding"):
            self.tiktoken_encoding = doc_processor_configer.tiktoken_encoding
        if self.counter not in _VALID_COUNTERS:
            raise ValueError(
                f"counter must be one of {sorted(_VALID_COUNTERS)}, "
                f"got '{self.counter}'.")
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
