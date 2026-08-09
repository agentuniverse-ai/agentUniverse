# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @Author  : contributor
# @FileName: duplicate_remover.py

"""
Exact-duplicate document remover (post-processor).

This processor drops documents whose text is an exact duplicate of one already
seen, identified by a SHA-256 content hash. It addresses the *exact dedup*
direction of issue #248.

Design notes
------------

* **Companion to SemanticDeduplicator.** ``SemanticDeduplicator`` removes
  *near*-duplicates via embeddings (heavy, fuzzy, needs a model).
  ``DuplicateRemover`` is the light, deterministic counterpart: it only drops
  *bit-for-bit identical* text and needs no model and no third-party
  dependency. Use it as a cheap first stage before any fuzzy dedup, or on its
  own when exact dedup is all that is required.
* **Stable, auditable.** Dedup is driven entirely by a SHA-256 hash, so the
  output is reproducible and the discarded documents are logged and (optionally)
  recorded in metadata for downstream audit.
* **Keep policy.** ``keep_first=True`` (default) retains the first occurrence of
  each duplicate group, preserving the original ranking from the store /
  earlier processors. ``keep_first=False`` retains the last occurrence, which is
  useful when later documents are fresher (e.g. a streaming append).
* **Configurable hash source.** By default the hash is computed from
  ``Document.text``. Set ``text_field`` to hash a metadata field instead
  (e.g. a normalized canonical id), and set ``hash_key`` to read a precomputed
  hash from metadata rather than recomputing one.
* **Normalization (opt-in).** Whitespace/case normalization before hashing is
  off by default so the contract is "exact text equality". Flip
  ``normalize_whitespace`` / ``ignore_case`` to collapse cosmetic differences
  that should not count as distinct content.
"""

import hashlib
import logging
import re
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

_WS_RE = re.compile(r"\s+")


class DuplicateRemover(DocProcessor):
    """Remove exact-duplicate documents using a SHA-256 content hash.

    Attributes:
        hash_key: Metadata key under which a precomputed hash is stored. When
            set, that value is used as the identity instead of recomputing a
            hash from the text. When unset (default), the hash is computed from
            the text (or ``text_field``).
        keep_first: When True (default) keep the first occurrence of each
            duplicate group; when False keep the last occurrence.
        text_field: Metadata key to read the hashing text from when
            ``Document.text`` is empty / when a custom canonical field should
            drive identity. Falls back to ``Document.text``.
        normalize_whitespace: Collapse all runs of whitespace to a single space
            and trim before hashing. Default False (true "exact" equality).
        ignore_case: Lowercase the text before hashing. Default False.
        record_stats_key: Metadata key under which per-document stats
            (``occurrence_index``, ``duplicate_group_size``) are stamped on
            every kept document. Set to None to skip.
        log_discarded: When True (default) log how many documents were dropped.
    """

    hash_key: Optional[str] = None
    keep_first: bool = True
    text_field: Optional[str] = None
    normalize_whitespace: bool = False
    ignore_case: bool = False
    record_stats_key: Optional[str] = "duplicate_stats"
    log_discarded: bool = True

    # ------------------------------------------------------------------ #
    # DocProcessor entry point
    # ------------------------------------------------------------------ #
    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Remove exact-duplicate documents.

        The algorithm makes a single pass over the input, computing (or
        reading) a stable identity for each document and keeping one
        representative per identity according to ``keep_first``. The number of
        discarded documents is logged.

        Args:
            origin_docs: Documents to deduplicate.
            query: Optional query (unused — dedup is content-intrinsic).

        Returns:
            Deduplicated document list. When ``keep_first`` is True the order
            of first occurrences is preserved; when False the order of last
            occurrences is preserved.
        """
        if not origin_docs:
            return []

        # Map identity -> list of (index, doc) for every occurrence.
        groups: Dict[str, List] = {}
        order: List[str] = []  # identities in first-seen order
        for idx, doc in enumerate(origin_docs):
            identity = self._identity(doc)
            if identity not in groups:
                groups[identity] = []
                order.append(identity)
            groups[identity].append((idx, doc))

        # Choose one representative per group.
        kept: List[Document] = []
        for identity in order:
            members = groups[identity]
            if self.keep_first:
                rep_idx, rep_doc = members[0]
            else:
                rep_idx, rep_doc = members[-1]
            self._stamp_stats(rep_doc, len(members))
            kept.append(rep_doc)

        # When keeping the last occurrence, restore the input order of those
        # last-occurrence documents so downstream ranking stays meaningful
        # (otherwise we'd return them in first-seen order, which is surprising).
        if not self.keep_first:
            kept = self._restore_input_order(kept, origin_docs)

        discarded = len(origin_docs) - len(kept)
        if self.log_discarded:
            logger.info(
                "DuplicateRemover[keep_first=%s]: %d in -> %d kept "
                "(dropped %d exact duplicates across %d groups)",
                self.keep_first, len(origin_docs), len(kept), discarded,
                len(order),
            )

        return kept

    # ------------------------------------------------------------------ #
    # Identity / hashing
    # ------------------------------------------------------------------ #
    def _identity(self, doc: Document) -> str:
        """Return a stable identity string for ``doc``.

        Order of resolution:
        1. ``hash_key`` metadata value, if configured and present.
        2. SHA-256 of the normalized text (``text_field`` metadata fallback).
        """
        if self.hash_key and doc.metadata:
            stored = doc.metadata.get(self.hash_key)
            if stored is not None and str(stored) != "":
                return str(stored)

        text = self._extract_text(doc)
        normalized = self._normalize(text)
        return self._sha256(normalized)

    def _extract_text(self, doc: Document) -> str:
        """Return the text to hash, with a metadata fallback."""
        if doc.text:
            return doc.text
        if self.text_field and doc.metadata:
            value = doc.metadata.get(self.text_field)
            if isinstance(value, str):
                return value
        return ""

    def _normalize(self, text: str) -> str:
        """Apply the configured normalization before hashing."""
        if not text:
            return ""
        if self.ignore_case:
            text = text.lower()
        if self.normalize_whitespace:
            text = _WS_RE.sub(" ", text).strip()
        return text

    @staticmethod
    def _sha256(text: str) -> str:
        """Return the hex SHA-256 digest of ``text`` (UTF-8 encoded)."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------ #
    # Metadata stamping
    # ------------------------------------------------------------------ #
    def _stamp_stats(self, doc: Document, group_size: int) -> None:
        """Record per-document dedup stats if a stats key is configured."""
        if not self.record_stats_key:
            return
        if doc.metadata is None:
            doc.metadata = {}
        existing = doc.metadata.get(self.record_stats_key)
        stats = dict(existing) if isinstance(existing, dict) else {}
        stats["duplicate_group_size"] = group_size
        doc.metadata[self.record_stats_key] = stats

    # ------------------------------------------------------------------ #
    # Ordering helper
    # ------------------------------------------------------------------ #
    @staticmethod
    def _restore_input_order(kept: List[Document],
                             origin_docs: List[Document]) -> List[Document]:
        """Return ``kept`` reordered to match their relative order in input."""
        kept_ids = {id(d) for d in kept}
        return [d for d in origin_docs if id(d) in kept_ids]

    # ------------------------------------------------------------------ #
    # Configuration loading
    # ------------------------------------------------------------------ #
    def _initialize_by_component_configer(
            self,
            doc_processor_configer: ComponentConfiger) -> 'DuplicateRemover':
        """Initialize remover parameters from the component configuration.

        Args:
            doc_processor_configer: Configuration object containing the
                remover parameters declared in the YAML.

        Returns:
            The initialized remover instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)

        if hasattr(doc_processor_configer, "hash_key"):
            self.hash_key = doc_processor_configer.hash_key
        if hasattr(doc_processor_configer, "keep_first"):
            self.keep_first = self._to_bool(doc_processor_configer.keep_first)
        if hasattr(doc_processor_configer, "text_field"):
            self.text_field = doc_processor_configer.text_field
        if hasattr(doc_processor_configer, "normalize_whitespace"):
            self.normalize_whitespace = self._to_bool(
                doc_processor_configer.normalize_whitespace)
        if hasattr(doc_processor_configer, "ignore_case"):
            self.ignore_case = self._to_bool(doc_processor_configer.ignore_case)
        if hasattr(doc_processor_configer, "record_stats_key"):
            self.record_stats_key = doc_processor_configer.record_stats_key
        if hasattr(doc_processor_configer, "log_discarded"):
            self.log_discarded = self._to_bool(doc_processor_configer.log_discarded)

        return self

    @staticmethod
    def _to_bool(value) -> bool:
        """Coerce YAML scalars to bool, handling string forms like 'false'.

        YAML loaders occasionally hand back strings (``"false"``) instead of
        native booleans. ``bool("false")`` would be ``True``, so this helper
        interprets the common falsy spellings explicitly before falling back to
        Python truthiness.
        """
        if isinstance(value, str):
            return value.strip().lower() not in {
                "false", "no", "off", "0", "", "none", "null"}
        return bool(value)
