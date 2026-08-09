# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: content_type_filter.py

"""
Content-type filter — a knowledge post-processing DocProcessor.

Filters recalled documents by the ``content_type`` field stored in their
metadata. This is useful for multi-modal or mixed-format knowledge bases
where an agent should only receive documents of a particular kind (for
example, only ``text`` chunks, only ``code``, or only ``table`` rows).

The filter is intentionally simple and dependency-free:

- Documents whose ``content_type`` is **in** ``allowed_types`` are kept.
- Documents whose ``content_type`` is present but **not** in
  ``allowed_types`` are dropped.
- Documents that have **no** ``content_type`` (or whose metadata is
  missing / the configured key is absent) follow ``default_policy``:
  ``"keep"`` retains them, ``"drop"`` removes them. Default is ``"keep"``
  (conservative — prefer false-keep over false-drop).

This mirrors the structure of ``LanguageFilter``: it subclasses
``DocProcessor``, reads its configuration from the component configer, and
exposes a pure-Python ``_process_docs`` implementation.

Addresses #248 (knowledge post-processing components).
"""

import logging
from typing import Any, List, Optional, Set

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

logger = logging.getLogger(__name__)

_VALID_POLICIES = ("keep", "drop")
_DEFAULT_TYPE_KEY = "content_type"
_DEFAULT_POLICY = "keep"


class ContentTypeFilter(DocProcessor):
    """Filter documents by their ``content_type`` metadata field.

    Attributes:
        allowed_types: Set of content-type strings to keep. Documents whose
            content type is in this set are retained. Default empty — when
            empty, the filter keeps everything (a no-op), which makes it
            safe to enable before configuring.
        type_key: Metadata key that holds the content type. Defaults to
            ``"content_type"``.
        default_policy: Policy for documents that have no content type.
            ``"keep"`` (default) retains them; ``"drop"`` removes them.
        case_sensitive: If True, content-type matching is case sensitive.
            Default False — content types like ``Text`` and ``text`` are
            treated as equal.
    """

    allowed_types: Set[str] = set()
    type_key: str = _DEFAULT_TYPE_KEY
    default_policy: str = _DEFAULT_POLICY
    case_sensitive: bool = False

    class Config:
        arbitrary_types_allowed = True

    # ------------------------------------------------------------------
    # Public DocProcessor entry point
    # ------------------------------------------------------------------
    def process_docs(self, origin_docs: List[Document],
                     query: Query = None) -> List[Document]:
        """Filter documents by content type, returning the kept subset."""
        self._validate_config()
        if not origin_docs:
            return []
        # An empty allow-list is a no-op (keep everything) so that enabling
        # the filter before populating allowed_types is safe.
        if not self.allowed_types:
            return list(origin_docs)

        normalized_allow = self._normalize_set(self.allowed_types)
        kept: List[Document] = []
        dropped = 0
        for doc in origin_docs:
            if self._should_keep(doc, normalized_allow):
                kept.append(doc)
            else:
                dropped += 1

        if dropped > 0:
            logger.debug(
                "ContentTypeFilter: dropped %d/%d documents "
                "(allowed: %s, policy for missing: %s)",
                dropped, len(origin_docs), normalized_allow, self.default_policy,
            )
        return kept

    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> List[Document]:
        """Implement the abstract DocProcessor method (delegates to process_docs)."""
        return self.process_docs(origin_docs, query)

    # ------------------------------------------------------------------
    # Decision logic
    # ------------------------------------------------------------------
    def _should_keep(self, doc: Document, normalized_allow: Set[str]) -> bool:
        """Return True if ``doc`` should be kept given the allow-list."""
        content_type = self._extract_content_type(doc)
        if content_type is None:
            # Missing content type -> apply default policy.
            return self.default_policy == "keep"
        value = content_type if self.case_sensitive else content_type.lower()
        return value in normalized_allow

    def _extract_content_type(self, doc: Document) -> Optional[str]:
        """Read the content type from the document's metadata.

        Returns the raw string value, or None when the field is absent or
        not a string. Leading/trailing whitespace is stripped.
        """
        metadata = getattr(doc, "metadata", None)
        if not isinstance(metadata, dict):
            return None
        if self.type_key not in metadata:
            return None
        value = metadata[self.type_key]
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        # Non-string scalars (int/float) are coerced to string so that a
        # numeric content-type id still works; everything else is ignored.
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
        return None

    # ------------------------------------------------------------------
    # Validation / normalization helpers
    # ------------------------------------------------------------------
    def _validate_config(self) -> None:
        if not isinstance(self.type_key, str) or not self.type_key.strip():
            raise ValueError("type_key must be a non-empty string")
        if self.default_policy not in _VALID_POLICIES:
            raise ValueError(
                f"default_policy must be one of {_VALID_POLICIES}, "
                f"got {self.default_policy!r}"
            )
        if not isinstance(self.case_sensitive, bool):
            raise ValueError("case_sensitive must be a boolean")

    def _normalize_set(self, values: Any) -> Set[str]:
        """Normalize the allowed set to comparable strings."""
        result: Set[str] = set()
        for value in values:
            if isinstance(value, str):
                normalized = value.strip()
                if not normalized:
                    continue
                result.add(normalized if self.case_sensitive else normalized.lower())
        return result

    # ------------------------------------------------------------------
    # Component configuration
    # ------------------------------------------------------------------
    def _initialize_by_component_configer(
        self, doc_processor_configer: ComponentConfiger
    ) -> "ContentTypeFilter":
        """Initialize the filter from a component configer (YAML)."""
        super()._initialize_by_component_configer(doc_processor_configer)
        allowed = getattr(doc_processor_configer, "allowed_types", None)
        if allowed is not None:
            self.allowed_types = set(allowed)
        type_key = getattr(doc_processor_configer, "type_key", None)
        if type_key is not None:
            self.type_key = type_key
        policy = getattr(doc_processor_configer, "default_policy", None)
        if policy is not None:
            self.default_policy = policy
        case_sensitive = getattr(doc_processor_configer, "case_sensitive", None)
        if case_sensitive is not None:
            self.case_sensitive = case_sensitive
        self._validate_config()
        return self
